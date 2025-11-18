# Render.com Start Command Configuration

## 🎯 Goal: Support Both Twilio Webhooks AND WebRTC WebSockets

---

## ✅ Recommended Start Command

```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT passenger_wsgi:application
```

---

## 📊 Comparison: gthread vs eventlet

### Current (gthread):
```bash
gunicorn --worker-class gthread -w 1 --threads 4 --bind 0.0.0.0:$PORT start_simple:app
```

| Feature | Support | Notes |
|---------|---------|-------|
| Twilio HTTP webhooks | ✅ Yes | Works fine |
| WebRTC WebSockets | ❌ **NO** | **Critical issue!** |
| Socket.IO | 🟡 Partial | Long-polling only, no WebSocket |
| Concurrency | 4 threads | Limited |
| Real-time performance | Moderate | Blocking I/O |

**Problem:** WebRTC voice assistant **won't work** because WebSocket upgrade fails.

---

### Recommended (eventlet):
```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT passenger_wsgi:application
```

| Feature | Support | Notes |
|---------|---------|-------|
| Twilio HTTP webhooks | ✅ Yes | Works perfectly |
| WebRTC WebSockets | ✅ **YES** | **Full support!** |
| Socket.IO | ✅ Full | WebSocket + long-polling |
| Concurrency | 1000s | Green threads |
| Real-time performance | Excellent | Non-blocking I/O |

**Benefit:** **Both** Twilio voice AND WebRTC voice work!

---

## 🔬 Technical Deep Dive

### What is eventlet?

Eventlet is a concurrent networking library that:
- Uses **green threads** (lightweight, cooperative multitasking)
- Provides **non-blocking I/O** (async operations)
- Supports **WebSocket protocol** (full duplex communication)
- Handles **1000s of concurrent connections** on single worker

### How eventlet handles different request types:

#### 1. **Regular HTTP (Twilio webhooks):**
```
Twilio → POST /convonet_todo/twilio/process_audio
    ↓
Gunicorn (eventlet worker) → Flask route
    ↓ (green thread)
Process request → Return TwiML
    ↓
Response to Twilio ✅
```
**Works perfectly!** Eventlet handles HTTP just like any other worker.

#### 2. **WebSocket (WebRTC Socket.IO):**
```
Browser → GET /socket.io/?transport=websocket
    ↓
Gunicorn (eventlet worker) → Upgrade to WebSocket
    ↓ (persistent green thread)
Socket.IO connection maintained
    ↓
Bidirectional communication ✅
```
**Only works with eventlet!** gthread can't upgrade to WebSocket.

---

## 🧪 Testing Both Features

### Test 1: Twilio Webhook (HTTP)

**Call your Twilio number:**
```
Phone → Twilio → Your server
POST /convonet_todo/twilio/call
```

**Expected:**
- Server logs: "Generated TwiML for incoming call"
- Phone receives: Voice prompts
- Works with eventlet: ✅

### Test 2: WebRTC Voice (WebSocket)

**Open browser:**
```
https://your-app.onrender.com/convonet_todo/webrtc/voice-assistant
```

**Expected:**
- Console: "✅ Connected to voice server"
- Network: 101 Switching Protocols
- Authentication works: ✅

---

## ⚙️ Configuration Differences

### Entry Point: `start_simple.py` vs `passenger_wsgi.py`

#### `start_simple.py` (Current):
```python
from app import create_app
app = create_app()
# No Socket.IO integration
```

**Issues:**
- Doesn't initialize Socket.IO properly
- No eventlet monkey patching
- gthread worker can't do WebSockets

#### `passenger_wsgi.py` (Recommended):
```python
import eventlet
eventlet.monkey_patch()  # Critical!

from app import create_app, socketio
app = create_app()
application = app
```

**Benefits:**
- ✅ Monkey patch enables green threads
- ✅ Socket.IO properly initialized
- ✅ eventlet worker supports WebSockets

---

## 🚀 Migration Steps

### Step 1: Update Render Dashboard

1. Go to: https://dashboard.render.com/
2. Select your service
3. Navigate to: **Settings** → **Build & Deploy**
4. Update **Start Command** to:
   ```bash
   gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT passenger_wsgi:application
   ```
5. Click **Save Changes**

### Step 2: Verify Environment Variables

Ensure these are set:
- `FLASK_KEY`
- `DB_URI`
- `OPENAI_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_OAUTH2_TOKEN_B64`

### Step 3: Manual Deploy

1. Click **Manual Deploy** → **Deploy latest commit**
2. Wait ~5 minutes for deployment

### Step 4: Check Logs

Look for:
```
[INFO] Starting gunicorn 21.2.0
[INFO] Using worker: eventlet          ← Must see this!
[INFO] Booting worker with pid: 123
✅ Eventlet monkey patch applied!
```

### Step 5: Test Both Features

**A. Test Twilio (HTTP):**
- Call your Twilio number
- Should work exactly as before ✅

**B. Test WebRTC (WebSocket):**
- Open voice assistant page
- Console: "✅ Connected to voice server" ✅
- Authenticate with PIN ✅
- Record and get response ✅

---

## 🤔 FAQ

### Q: Will Twilio webhooks still work with eventlet?
**A:** ✅ **YES!** Eventlet handles all HTTP requests perfectly, including POST requests from Twilio.

### Q: Is eventlet slower than gthread for HTTP?
**A:** No! For I/O-bound operations (webhooks, API calls), eventlet is often **faster** because of non-blocking I/O.

### Q: What about the 4 threads from gthread?
**A:** Eventlet's green threads provide **much more** concurrency (1000s) than 4 OS threads.

### Q: Do I need to change any code?
**A:** No! Your Twilio routes work as-is. The change is only in how Gunicorn runs the app.

### Q: What if eventlet breaks something?
**A:** Extremely unlikely. But you can always rollback in Render dashboard:
1. Go to **Events** tab
2. Find previous deploy
3. Click **Rollback**

---

## 📊 Performance Comparison

| Metric | gthread (4 threads) | eventlet (green threads) |
|--------|---------------------|-------------------------|
| **Concurrent connections** | ~40 | ~1000+ |
| **Memory per connection** | ~2MB | ~4KB |
| **WebSocket support** | ❌ No | ✅ Yes |
| **I/O blocking** | Yes | No (async) |
| **Twilio webhooks** | ✅ Works | ✅ Works |
| **WebRTC voice** | ❌ Fails | ✅ Works |

**Verdict:** eventlet is superior for this use case!

---

## 🎯 Bottom Line

### Current Setup:
```bash
gunicorn --worker-class gthread -w 1 --threads 4 start_simple:app
```
- ✅ Twilio works
- ❌ WebRTC doesn't work

### Recommended Setup:
```bash
gunicorn --worker-class eventlet -w 1 passenger_wsgi:application
```
- ✅ Twilio works
- ✅ WebRTC works
- ✅ Better performance
- ✅ More scalable

---

## ✅ Action Items

1. **Update Start Command** in Render dashboard (see above)
2. **Redeploy** your service
3. **Test Twilio** (call your number)
4. **Test WebRTC** (open voice assistant page)
5. **Verify both work** ✅

---

**Ready to switch?** The migration is safe and will make WebRTC work while keeping Twilio functional! 🚀

---

**P.S.** If you're nervous about the change, you can:
1. Test locally first: `gunicorn --worker-class eventlet -w 1 passenger_wsgi:application`
2. Deploy to a test Render service
3. Then update production once confirmed

But honestly, it's very safe. Eventlet is the recommended worker for Flask-SocketIO! ✨

