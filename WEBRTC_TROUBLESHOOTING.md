# WebRTC Voice Assistant Troubleshooting

## 🐛 Issue: "Authenticate Button Does Nothing"

### Quick Fix Steps

1. **Open Browser Console** (Press F12)
2. **Refresh the page**
3. **Look for connection messages**

---

## 🔍 Diagnostic Messages

### What You Should See on Page Load:

```
🔌 Initializing Socket.IO connection...
✅ Connected to voice server
📢 Status [success]: Connected! Ready to authenticate.
```

### What Indicates a Problem:

```
❌ Connection error: ...
📢 Status [error]: Connection error. Please refresh the page.
```

---

## 🛠️ Common Issues & Solutions

### Issue 1: Socket.IO Not Connecting

**Symptoms:**
- Authenticate button does nothing
- Console shows: `❌ Connection error`
- Status says: "Connection error. Please refresh the page."

**Causes:**
1. Server not running Socket.IO properly
2. CORS issues
3. Port mismatch

**Solutions:**

#### Check Server is Running:
```bash
# On server, check if app is running
ps aux | grep python

# Check if Socket.IO is loaded
curl https://hjlees.com/convonet_todo/webrtc/voice-assistant
# Should return HTML with Socket.IO script tag
```

#### Check Socket.IO CDN:
Look in browser console for:
```
GET https://cdn.socket.io/4.5.4/socket.io.min.js
```
If this fails, Socket.IO library didn't load.

#### Verify Server Configuration:
```python
# In app.py, should have:
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# In passenger_wsgi.py, should have:
application = socketio.wsgi_app if socketio else app
```

---

### Issue 2: Socket Connects but Authenticate Fails

**Symptoms:**
- Console shows: `✅ Connected to voice server`
- Click Authenticate → Nothing happens
- Console shows: `🔐 Authenticate button clicked`
- But no `📤 Sending authentication request`

**Cause:**
Socket connection was lost after initial connect.

**Solution:**
```javascript
// Check socket status in console:
socket.connected
// Should return: true

// If false, refresh the page
```

---

### Issue 3: PIN Validation Error

**Symptoms:**
- Console shows: `❌ Invalid PIN length: X`
- Status says: "Please enter a valid PIN (4-6 digits)"

**Cause:**
PIN is less than 4 digits.

**Solution:**
Enter a PIN with 4-6 digits (e.g., `1234`).

---

### Issue 4: Authentication Request Sent but No Response

**Symptoms:**
- Console shows: `📤 Sending authentication request`
- Status says: "Authenticating..."
- But nothing happens (stuck)

**Causes:**
1. Server not handling `authenticate` event
2. Database connection error
3. User with that PIN doesn't exist

**Debug on Server:**
```bash
# Check server logs for:
"🔐 Authentication request for session XXX: PIN=1234"

# If you see this, check for database errors
# If you don't see this, Socket.IO event handler not registered
```

**Solutions:**

#### Verify init_socketio is called:
```python
# In app.py, should have:
from convonet.webrtc_voice_server import webrtc_bp, init_socketio
app.register_blueprint(webrtc_bp)
init_socketio(socketio)  # ← This line is critical!
```

#### Check User Exists:
```bash
# Run on server:
python check_admin_user.py

# Should show user with voice_pin=1234
```

---

### Issue 5: "Not connected to server" Message

**Symptoms:**
- Click Authenticate
- Status says: "Not connected to server. Please refresh the page."
- Console shows: `❌ Socket not connected: null`

**Cause:**
Socket.IO never connected or was disconnected.

**Solution:**
1. Refresh the page
2. Wait 2-3 seconds for connection
3. Look for `✅ Connected to voice server`
4. Then try authenticating again

---

## 🔧 Advanced Debugging

### Enable Detailed Socket.IO Logging

Add to browser console:
```javascript
localStorage.debug = '*';
// Then refresh the page
```

This shows all Socket.IO events and messages.

### Check Network Tab

1. Open DevTools → Network tab
2. Refresh page
3. Look for:
   - `socket.io/?EIO=4&transport=polling` (should be 101 Switching Protocols)
   - Or `socket.io/?EIO=4&transport=websocket` (should be successful)

If these show errors, Socket.IO can't connect.

### Test Socket.IO Directly

In browser console:
```javascript
// After page loads:
socket.emit('test', { message: 'hello' });

// Check server logs for 'test' event
```

---

## ✅ Expected Working Flow

### 1. Page Load
```
Browser Console:
🔌 Initializing Socket.IO connection...
✅ Connected to voice server

Page Status:
"Connected! Ready to authenticate." (green)
```

### 2. Enter PIN
```
Browser Console:
(nothing yet)

Page:
PIN input field has value: "1234"
```

### 3. Click Authenticate
```
Browser Console:
🔐 Authenticate button clicked
📤 Sending authentication request with PIN

Page Status:
"Authenticating..." (blue)
```

### 4. Server Processes
```
Server Logs:
🔐 Authentication request for session abc123: PIN=1234
✅ Authentication successful: admin@convonet.com
```

### 5. Success Response
```
Browser Console:
📢 Status [success]: Welcome back, Admin!

Page:
Auth section disappears
Voice section appears
Microphone button enabled
Status: "Ready"
```

---

## 🚨 Emergency Fallback

If WebRTC won't work after all troubleshooting:

### Use Twilio Voice Instead:
```
Call: +1 (XXX) XXX-XXXX
Press 1234#
Speak your commands
```

Twilio voice still works as a fallback!

---

## 📊 Checklist for Deployment

Before going live, verify:

- [ ] `app.py` has `socketio = SocketIO(...)` initialization
- [ ] `app.py` calls `init_socketio(socketio)`
- [ ] `passenger_wsgi.py` exports `socketio.wsgi_app`
- [ ] Server has `Flask-SocketIO>=5.0.0` installed
- [ ] User with voice_pin exists in database
- [ ] HTTPS enabled (required for microphone access)
- [ ] CORS enabled for Socket.IO
- [ ] Port 10000 accessible
- [ ] Logs show "✅ MCP client initialized successfully"

---

## 💡 Pro Tips

### Test Locally First
```bash
# Run locally:
python app.py

# Open:
http://localhost:10000/convonet_todo/webrtc/voice-assistant

# Should work without HTTPS locally
```

### Monitor Real-Time
Keep server logs and browser console open side-by-side:
```
Left: Server terminal (python app.py)
Right: Browser console (F12)
```

Watch messages flow in real-time.

### Common Port Issues
If using Render.com:
- They assign port dynamically via `PORT` env variable
- Socket.IO should auto-detect this
- Check `app.py` uses `port=int(os.getenv('PORT', 10000))`

---

## 📞 Still Having Issues?

### Gather This Info:

1. **Browser Console Output** (copy all messages)
2. **Network Tab** (WebSocket/polling requests)
3. **Server Logs** (last 50 lines)
4. **Environment**:
   - Browser: Chrome/Firefox/Safari?
   - OS: Mac/Windows/Linux?
   - HTTPS: Yes/No?

### Test Cases to Try:

1. **Different Browser**
   - Chrome → Firefox
   - Desktop → Mobile

2. **Incognito Mode**
   - Clears cache
   - No extensions

3. **Different Network**
   - WiFi → Mobile data
   - Check firewall

---

**Built for SambaNova Hackathon**

*Need help? Check server logs first, then browser console!*

