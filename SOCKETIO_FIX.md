# Socket.IO WebSocket Fix

## 🐛 The Problem

```
AttributeError: 'Response' object has no attribute 'status_code'
GET /socket.io/?EIO=4&transport=websocket HTTP/1.1 500
```

**What happened:**
- Browser tried to connect to Socket.IO via WebSocket
- Gunicorn received WebSocket upgrade request
- Gunicorn's default worker (sync) doesn't support WebSockets
- Gunicorn crashed with AttributeError

**User Impact:**
- WebRTC voice assistant page loads ✅
- But Socket.IO won't connect ❌
- Authenticate button does nothing ❌
- Console shows connection error ❌

---

## 🔧 The Fix

### 1. **Change Flask-SocketIO to use eventlet**

**Before:**
```python
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
```

**After:**
```python
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
```

**Why:**
- `threading` mode is for development only
- `eventlet` supports WebSockets in production
- Works with Gunicorn's eventlet worker class

---

### 2. **Add eventlet monkey patching**

**File:** `passenger_wsgi.py`

**Added at the very top:**
```python
import eventlet
eventlet.monkey_patch()
```

**Why this must be first:**
- Monkey patching replaces Python's standard library
- Patches socket, threading, time, etc. to be non-blocking
- MUST happen before importing anything else
- If other modules import first, they'll use blocking versions

---

### 3. **Update Procfile to use eventlet worker**

**Before:**
```
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT wsgi_to_asgi_converter:asgi_app
```

**After:**
```
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT passenger_wsgi:application
```

**Changes:**
- `--worker-class eventlet` tells Gunicorn to use eventlet workers
- `-w 1` means single worker (REQUIRED for Socket.IO)
- `passenger_wsgi:application` points to our WSGI app

**Why single worker?**
Socket.IO requires sticky sessions. With multiple workers:
- Client connects to worker A
- Next request might go to worker B
- Worker B doesn't have the session → connection fails
- Solution: Use 1 worker OR Redis for session sharing

---

### 4. **Simplified application export**

**Before:**
```python
application = socketio.wsgi_app if socketio else app
```

**After:**
```python
application = app
```

**Why:**
- Flask-SocketIO integrates via `socketio.init_app(app)`
- Middleware is already attached to the Flask app
- No need to export `socketio.wsgi_app` separately
- Gunicorn with eventlet worker handles everything

---

## 📊 How It Works

### Gunicorn Worker Classes

| Worker Class | WebSocket Support | Use Case |
|--------------|-------------------|----------|
| `sync` (default) | ❌ No | Simple HTTP only |
| `gevent` | ✅ Yes | WebSockets, async |
| `eventlet` | ✅ Yes | WebSockets, async |
| `tornado` | ✅ Yes | WebSockets, async |

**We chose eventlet because:**
- Official Flask-SocketIO recommendation
- Excellent WebSocket support
- Lightweight green threads
- Easy to use with monkey patching

---

### The Complete Flow

#### Before (Broken):

```
Browser → WebSocket Upgrade Request
    ↓
Gunicorn (sync worker) → "What's a WebSocket?"
    ↓
Tries to treat it as HTTP
    ↓
Response object has no status_code
    ↓
❌ AttributeError: 'Response' object has no attribute 'status_code'
```

#### After (Fixed):

```
Browser → WebSocket Upgrade Request
    ↓
Gunicorn (eventlet worker) → "I know WebSockets!"
    ↓
Eventlet handles upgrade
    ↓
Socket.IO connection established
    ↓
✅ Browser console: "Connected to voice server"
```

---

## 🧪 Testing

### Expected Behavior After Deploy:

1. **Page Load:**
   - Browser loads: https://hjlees.com/sambanova_todo/webrtc/voice-assistant
   - JavaScript tries to connect: `io('/voice')`
   - Request sent: `GET /socket.io/?EIO=4&transport=websocket`

2. **Server Response:**
   - **Before:** `500 Internal Server Error`
   - **After:** `101 Switching Protocols` ✅

3. **Browser Console:**
   - **Before:** `❌ Connection error`
   - **After:** `✅ Connected to voice server` ✅

4. **Authenticate Button:**
   - **Before:** Does nothing (no connection)
   - **After:** Sends PIN to server, gets response ✅

---

## 🔍 Debugging

### Check if eventlet is loaded:

**Server logs should show:**
```
[INFO] Starting gunicorn 21.2.0
[INFO] Using worker: eventlet
[INFO] Booting worker with pid: 123
```

If you see `Using worker: sync` → **WRONG!** Eventlet not loading.

### Check WebSocket upgrade:

**Browser Network Tab:**
```
Request URL: wss://hjlees.com/socket.io/?EIO=4&transport=websocket
Status: 101 Switching Protocols
```

If status is `500` or `502` → Still broken.

### Check monkey patching:

**Add to passenger_wsgi.py temporarily:**
```python
import eventlet
eventlet.monkey_patch()
print("✅ Eventlet monkey patch applied!")
```

Check logs for this message.

---

## ⚠️ Important Notes

### 1. **Order matters!**

This will **BREAK**:
```python
from app import create_app  # ❌ Imports before monkey patch
import eventlet
eventlet.monkey_patch()
```

This will **WORK**:
```python
import eventlet
eventlet.monkey_patch()  # ✅ First!
from app import create_app
```

### 2. **Single worker limitation**

Currently using `-w 1` (single worker):
- **Pro:** Simple, works out of the box
- **Con:** Limited concurrency (~1000 connections)

For production at scale:
- Use Redis for session storage
- Enable multiple workers: `-w 4`
- Configure Socket.IO to use Redis adapter

### 3. **Eventlet vs Gevent**

Both work, but eventlet is recommended:

| Feature | Eventlet | Gevent |
|---------|----------|--------|
| Official support | ✅ Yes | ✅ Yes |
| Monkey patching | Simple | More complex |
| Community | Larger | Smaller |
| Performance | Good | Slightly faster |

**Stick with eventlet unless you have specific needs.**

---

## 📚 References

- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- [Gunicorn Design](https://docs.gunicorn.org/en/stable/design.html)
- [Eventlet Documentation](https://eventlet.net/)

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Page loads: https://hjlees.com/sambanova_todo/webrtc/voice-assistant
- [ ] Browser console: `✅ Connected to voice server`
- [ ] Status message: "Connected! Ready to authenticate." (green)
- [ ] Enter PIN: 1234
- [ ] Click Authenticate button
- [ ] Auth section hides, voice UI appears
- [ ] Microphone button is enabled

If all checks pass → **🎉 WebRTC voice is working!**

---

## 🚀 Next Steps

1. **Wait ~5 minutes** for Render.com to deploy
2. **Refresh** the voice assistant page
3. **Open console** (F12) to see connection status
4. **Test authentication** with PIN: 1234
5. **Start using** WebRTC voice assistant!

---

**Fixed in commit:** `c477790`

*Because "AttributeError: 'Response' object has no attribute 'status_code'" should be "101 Switching Protocols"!* ✨

