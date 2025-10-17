# Switched from SIP.js to JsSIP

## What Changed

I've migrated your call center from SIP.js to JsSIP because:
- ✅ More reliable CDN availability
- ✅ Simpler API
- ✅ Better WebRTC support
- ✅ Smaller file size

## Files Updated

1. **`call_center/templates/call_center.html`**
   - Changed CDN from SIP.js to JsSIP
   - Added fallback CDN loading
   - Added compatibility checks

2. **`call_center/static/js/call_center.js`**
   - Updated `initSIPClient()` to use JsSIP API
   - Updated `handleIncomingCall()` to use JsSIP session objects
   - Fixed call ID extraction

## How to Test

### Step 1: Restart Flask App

```bash
# Stop current app (Ctrl+C)
# Then restart:
cd "/Users/hj/Web Development Projects/1. Main"
python app.py
```

### Step 2: Clear Browser Cache

```
Chrome: Ctrl+Shift+Delete → Clear cache
Firefox: Ctrl+Shift+Delete → Clear cache  
Safari: Cmd+Option+E
```

### Step 3: Access Call Center

```
Open: http://localhost:10000/call-center/
```

### Step 4: Check Console

Open browser console (F12) and look for:
```
✓ JsSIP loaded successfully
Initializing SIP client for 2000@34.26.59.14
```

### Step 5: Login

```
Extension: 2000
Username: 2000
Password: your_password
SIP Domain: 34.26.59.14
```

## Expected Console Output

When login is successful:
```
✓ JsSIP loaded successfully
Initializing SIP client for 2000@34.26.59.14
SIP User Agent started
✓ SIP connected
✓ SIP registered
```

## If Still Not Working

### Check 1: JsSIP Loaded?

In browser console:
```javascript
console.log(typeof JsSIP);
// Should show: "object"
```

### Check 2: WebSocket Connection

Check console for WebSocket errors:
```
WebSocket connection to 'wss://34.26.59.14:7443' failed: ...
```

If you see this, the issue is FreePBX WebSocket configuration (see FREEPBX_WEBRTC_TROUBLESHOOTING.md)

### Check 3: SIP Registration

Check console for:
```
✗ SIP registration failed: 401 Unauthorized
```

If you see this, credentials are wrong or extension doesn't exist.

## JsSIP vs SIP.js Differences

| Feature | SIP.js | JsSIP |
|---------|--------|-------|
| User Agent | `new SIP.UserAgent()` | `new JsSIP.UA()` |
| Transport | `transportOptions` | `WebSocketInterface` |
| Session | `invitation` | `session` |
| Remote ID | `remoteIdentity` | `remote_identity` |
| Call ID | `request.callId` | `id` |

## Advantages of JsSIP

1. **More reliable CDN**: jsdelivr + GitHub fallback
2. **Smaller size**: ~60KB vs ~200KB
3. **Simpler API**: Fewer abstractions
4. **Better documented**: More examples online
5. **Active development**: Regular updates

## Troubleshooting

### Issue: "JsSIP is not defined"

**Cause:** CDN blocked or slow internet

**Solution:**
1. Check internet connection
2. Disable ad blockers
3. Try different browser
4. Wait and refresh (CDN might be slow)

### Issue: "WebSocket connection failed"

**Cause:** FreePBX WebSocket not configured

**Solution:** See `FREEPBX_WEBRTC_TROUBLESHOOTING.md`

### Issue: "401 Unauthorized"

**Cause:** Wrong credentials

**Solution:**
1. Check extension 2000 exists in FreePBX
2. Verify username/password match
3. Check FreePBX logs: `/var/log/asterisk/full`

## Next Steps

1. ✅ Test login with extension 2000
2. ✅ Make a test call
3. ✅ Verify audio works
4. ✅ Test incoming call handling

## References

- JsSIP Documentation: https://jssip.net/documentation/
- JsSIP GitHub: https://github.com/versatica/JsSIP
- FreePBX WebRTC: See `FREEPBX_WEBRTC_TROUBLESHOOTING.md`

