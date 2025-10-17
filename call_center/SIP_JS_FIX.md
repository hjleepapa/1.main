# SIP.js "SIP is not defined" Error - Fix Guide

## Problem
```
ReferenceError: SIP is not defined at CallCenterAgent.initSIPClient
```

## Root Cause
The SIP.js library is not loading properly or not exposing the global `SIP` object.

---

## Solution 1: Use SIP.js 0.20.0 (Already Applied)

I've updated your `call_center.html` to use version 0.20.0 which has better CDN support:

```html
<script src="https://cdn.jsdelivr.net/npm/sip.js@0.20.0/dist/sip.min.js"></script>
```

**Test it:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Refresh the page
3. Open browser console (F12)
4. You should see: "SIP.js loaded successfully:"
5. Try logging in

---

## Solution 2: Use Alternative CDN

If Solution 1 doesn't work, try unpkg.com CDN:

```html
<!-- Replace line 216 in call_center.html with: -->
<script src="https://unpkg.com/sip.js@0.20.0/dist/sip.min.js"></script>
```

---

## Solution 3: Download and Host Locally

Download SIP.js and serve it from your own server:

### Step 1: Download SIP.js

```bash
cd "/Users/hj/Web Development Projects/1. Main/call_center/static/js"

# Download SIP.js
curl -o sip.min.js https://cdn.jsdelivr.net/npm/sip.js@0.20.0/dist/sip.min.js

# Verify file was downloaded
ls -lh sip.min.js
```

### Step 2: Update HTML

Edit `call_center/templates/call_center.html`:

```html
<!-- Replace CDN link with local file: -->
<script src="{{ url_for('call_center.static', filename='js/sip.min.js') }}"></script>
```

---

## Solution 4: Use JsSIP Instead (Alternative Library)

If SIP.js continues to cause issues, use JsSIP which is more lightweight:

### Step 1: Update HTML

```html
<!-- Replace SIP.js with JsSIP -->
<script src="https://cdn.jsdelivr.net/npm/jssip@3.10.1/dist/jssip.min.js"></script>
```

### Step 2: Update call_center.js

You'll need to rewrite the SIP client code to use JsSIP API instead. Here's a quick example:

```javascript
initSIPClient(username, password, domain) {
    const socket = new JsSIP.WebSocketInterface(`wss://${domain}:7443`);
    
    const configuration = {
        sockets: [socket],
        uri: `sip:${username}@${domain}`,
        password: password,
        display_name: username
    };
    
    this.sipUA = new JsSIP.UA(configuration);
    
    this.sipUA.on('connected', () => {
        console.log('SIP connected');
        this.updateSIPStatus('connected');
    });
    
    this.sipUA.on('disconnected', () => {
        console.log('SIP disconnected');
        this.updateSIPStatus('disconnected');
    });
    
    this.sipUA.on('newRTCSession', (data) => {
        this.handleIncomingCall(data.session);
    });
    
    this.sipUA.start();
}
```

---

## Debugging Steps

### Check 1: Verify SIP.js Loads

Open browser console and run:

```javascript
console.log(typeof SIP);
console.log(SIP);
```

**Expected:** `object` and SIP object details  
**If undefined:** Library didn't load

### Check 2: Check Network Tab

1. Open Developer Tools (F12)
2. Go to Network tab
3. Refresh page
4. Look for `sip.min.js` request
5. Check if it loads successfully (Status 200)
6. Click on it and check Response tab

**If 404 or failed:** CDN issue or network problem

### Check 3: Check for CORS Errors

Look in console for errors like:
```
Access to script at 'https://cdn.jsdelivr.net/...' blocked by CORS policy
```

**Solution:** Use Solution 3 (host locally)

### Check 4: Check CSP Headers

If you have Content Security Policy, you might need to allow the CDN:

```html
<meta http-equiv="Content-Security-Policy" 
      content="script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'unsafe-inline'">
```

---

## Quick Test Page

Create a test HTML file to verify SIP.js loads:

```html
<!DOCTYPE html>
<html>
<head>
    <title>SIP.js Test</title>
</head>
<body>
    <h1>SIP.js Library Test</h1>
    <div id="result"></div>
    
    <script src="https://cdn.jsdelivr.net/npm/sip.js@0.20.0/dist/sip.min.js"></script>
    <script>
        window.addEventListener('load', function() {
            const resultDiv = document.getElementById('result');
            
            if (typeof SIP !== 'undefined') {
                resultDiv.innerHTML = '<h2 style="color: green;">✓ SIP.js loaded successfully!</h2>';
                resultDiv.innerHTML += '<pre>' + JSON.stringify(Object.keys(SIP), null, 2) + '</pre>';
            } else {
                resultDiv.innerHTML = '<h2 style="color: red;">✗ SIP.js NOT loaded!</h2>';
                resultDiv.innerHTML += '<p>Check browser console for errors.</p>';
            }
        });
    </script>
</body>
</html>
```

Save as `sip_test.html` and open in browser.

---

## Browser Compatibility Issues

### Issue: Browser Blocks CDN

Some corporate firewalls or browser extensions block CDN:

**Solution:**
- Disable ad blockers
- Try in incognito/private mode
- Host locally (Solution 3)

### Issue: Old Browser

SIP.js requires modern browser features:

**Minimum requirements:**
- Chrome 74+
- Firefox 66+
- Safari 12.1+
- Edge 79+

---

## Recommended Fix (Step by Step)

### 1. Clear Browser Cache

```
Chrome: Ctrl+Shift+Delete → Clear browsing data
Firefox: Ctrl+Shift+Delete → Clear Data
Safari: Cmd+Option+E
```

### 2. Check Console

```
F12 → Console tab
Refresh page
Look for "SIP.js loaded successfully:"
```

### 3. If Still Not Working - Download Locally

```bash
cd "/Users/hj/Web Development Projects/1. Main/call_center/static/js"
curl -o sip.min.js https://cdn.jsdelivr.net/npm/sip.js@0.20.0/dist/sip.min.js
```

Then update HTML:
```html
<script src="{{ url_for('call_center.static', filename='js/sip.min.js') }}"></script>
```

### 4. Restart Flask App

```bash
# Stop current app (Ctrl+C)
python app.py
```

### 5. Test Again

```
Open: http://localhost:10000/call-center/
Login with your credentials
Check console for errors
```

---

## Alternative: Use WebRTC Without SIP.js

If SIP.js continues to be problematic, you can use native WebRTC:

```javascript
// Simple WebRTC without SIP.js
const pc = new RTCPeerConnection({
    iceServers: [{urls: 'stun:stun.l.google.com:19302'}]
});

// Get user media
navigator.mediaDevices.getUserMedia({audio: true})
    .then(stream => {
        stream.getTracks().forEach(track => pc.addTrack(track, stream));
    });
```

But this requires more manual SIP signaling implementation.

---

## Summary

**Quick Fix (Already Applied):**
```html
<!-- Changed from 0.21.2 to 0.20.0 -->
<script src="https://cdn.jsdelivr.net/npm/sip.js@0.20.0/dist/sip.min.js"></script>
```

**If still broken:**
1. Clear browser cache
2. Check console for "SIP.js loaded successfully"
3. Download and host locally if CDN blocked
4. Consider JsSIP as alternative

**Most likely cause:** Browser cache or CDN blocked by firewall/extension

