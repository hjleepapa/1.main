# Troubleshooting: Agent Not Receiving Incoming Calls

## Problem
FusionPBX is routing the call to extension 2001, but the agent dashboard is not receiving the call event (`newRTCSession` is not firing).

## Symptoms
- FusionPBX logs show: `sofia/internal/6ndsn66p@d82mad3805n8.invalid sending invite`
- Session is created but remains "Locked, Waiting on external entities"
- After 30 seconds, call times out and goes to voicemail
- No `newRTCSession` event in browser console
- No customer popup appears

## Root Causes

### 1. Agent Dashboard Not Open or SIP Client Not Registered

**Check:**
1. Open the agent dashboard: `https://hjlees.com/call-center/`
2. Log in with extension 2001 credentials
3. Check browser console for:
   ```
   ✓ SIP connected
   ✓ SIP registered
   ```

**If not registered:**
- Check SIP credentials (username, password, domain)
- Verify WebSocket connection: `wss://pbx.hjlees.com:7443`
- Check for registration errors in console

### 2. WebSocket Connection Dropped

**Check:**
1. Open browser console (F12)
2. Look for WebSocket errors:
   ```
   WebSocket connection to 'wss://pbx.hjlees.com:7443' failed
   ```
3. Check Network tab for WebSocket connection status

**Fix:**
- Refresh the agent dashboard page
- Re-login to re-establish SIP registration
- Check FusionPBX WebSocket configuration

### 3. SIP Registration Expired

**Check:**
1. In browser console, look for:
   ```
   SIP unregistered
   ```
2. Check if registration is still active

**Fix:**
- JsSIP should auto-renew registration every 600 seconds
- If registration fails, check FusionPBX extension settings
- Verify extension 2001 exists and is enabled

### 4. Contact URI Mismatch

**Issue:** FusionPBX sends INVITE to registered contact URI, but it doesn't match.

**Check FusionPBX logs:**
```
sofia/internal/6ndsn66p@d82mad3805n8.invalid sending invite
```

**Check browser console:**
- Look for the registered contact URI in JsSIP logs
- Verify it matches what FusionPBX is using

## Debugging Steps

### Step 1: Verify Agent Dashboard is Open and Registered

1. Open agent dashboard
2. Log in
3. Check console for:
   ```
   ✓ JsSIP v3.10.1 loaded successfully
   Initializing SIP client for 2001@pbx.hjlees.com
   ✓ SIP connected
   ✓ SIP registered
   ```

### Step 2: Monitor Browser Console During Transfer

1. Keep browser console open
2. Initiate transfer from voice assistant
3. Watch for:
   ```
   🔔 New RTC session event received
   📞 Incoming call detected, handling...
   ```

**If you don't see these messages:**
- The INVITE is not reaching the browser
- Check WebSocket connection
- Check SIP registration status

### Step 3: Check FusionPBX Registration Status

On FusionPBX server:
```bash
fs_cli -x "sofia_contact 2001@pbx.hjlees.com"
```

**Expected output:**
```
sofia/internal/6ndsn66p@d82mad3805n8.invalid;transport=ws
```

**If no output:**
- Extension 2001 is not registered
- Agent dashboard SIP client is not connected

### Step 4: Check FusionPBX Logs in Real-Time

On FusionPBX server:
```bash
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2001|6ndsn66p|invite"
```

**What to look for:**
- `sending invite` - FusionPBX is trying to deliver the call
- `Session ... Locked, Waiting on external entities` - Call is waiting for agent to respond
- `Hangup ... NORMAL_CLEARING` - Call timed out

## Quick Fixes

### Fix 1: Refresh Agent Dashboard
1. Refresh the browser page
2. Re-login
3. Wait for "✓ SIP registered" message
4. Try transfer again

### Fix 2: Check SIP Registration
1. In browser console, run:
   ```javascript
   // Check if SIP client is registered
   console.log('SIP UA:', window.callCenterAgent?.sipUser);
   console.log('Is registered:', window.callCenterAgent?.sipUser?.isRegistered());
   ```

### Fix 3: Restart SIP Client
1. In browser console, run:
   ```javascript
   // Stop current SIP client
   if (window.callCenterAgent?.sipUser) {
       window.callCenterAgent.sipUser.stop();
   }
   // Re-initialize (will happen on page refresh)
   ```

## Prevention

1. **Keep Agent Dashboard Open:** The dashboard must be open and registered to receive calls
2. **Monitor Registration:** Check console periodically for "SIP unregistered" messages
3. **Auto-Refresh:** Consider adding auto-refresh if registration fails
4. **Connection Monitoring:** Add WebSocket reconnection logic

## Additional Logging

The code now includes enhanced logging:
- `[VoiceAssistantBridge]` - Transfer bridge endpoint logs
- `🔔 New RTC session event received` - Browser console when call arrives
- `📋 Cached customer profile` - Customer data caching logs

Check application logs and browser console for these messages to trace the call flow.

