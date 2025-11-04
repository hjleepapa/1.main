# WebRTC to FusionPBX Direct Transfer Guide

## Current Status

**Question:** Can the WebRTC call on https://hjlees.com/sambanova_todo/webrtc/voice-assistant be transferred directly to extension 2001@136.115.41.45 in FusionPBX?

**Answer:** **Currently NO** - Direct transfer is not implemented. Additional components/implementation are required.

## 🔍 Current Implementation

Based on your logs and code, here's what currently happens:

### When Transfer is Requested:

1. ✅ User says "transfer me to human agent"
2. ✅ AI detects request and calls `transfer_to_agent()` tool
3. ✅ Tool returns `TRANSFER_INITIATED:2001|support|...`
4. ✅ WebRTC server sends Socket.IO event `transfer_initiated` to client
5. ❌ **Client is shown manual transfer instructions** (Twilio phone number or SIP URI)
6. ❌ **User must manually initiate a new call** - the WebRTC call is NOT bridged

### Current Transfer Options Provided:

From `webrtc_voice_server.py`, the system currently provides:
- **Option 1:** Call Twilio number and request transfer
- **Option 2:** Use SIP client (Zoiper, Linphone) with provided SIP URI

**The WebRTC call itself is NOT bridged to FusionPBX.**

## 🎯 What Would Be Needed for Direct Transfer

To enable **direct WebRTC-to-SIP bridging**, you would need one of these approaches:

### Option 1: FusionPBX WebRTC Support (Recommended)

Since FusionPBX is based on FreeSWITCH, which supports WebRTC, you could:

#### Architecture:
```
WebRTC Client (Browser) 
    ↓ WebRTC (WSS)
Your Server (Bridge Node)
    ↓ SIP
FusionPBX → Extension 2001
```

#### Requirements:

1. **Configure FusionPBX WebRTC Profile:**
   - FusionPBX has WebRTC support via FreeSWITCH
   - Need to enable WSS (WebSocket Secure) SIP profile
   - Port: 7443 (default WebRTC port)

2. **Implement Server-Side SIP Bridge:**
   - Use Python SIP library (e.g., `pjsua-python`, `aiortc`, or `pyVoIP`)
   - Bridge WebRTC media stream to SIP call
   - Handle media transcoding (if needed)

3. **Implementation Steps:**
   ```python
   # Pseudo-code for WebRTC-to-SIP bridge
   import pjsua as pj
   
   def bridge_webrtc_to_sip(webrtc_session, extension):
       # Create SIP call to FusionPBX
       sip_call = create_sip_call(
           destination=f"sip:{extension}@136.115.41.45",
           from_uri="sip:webrtc@your-server.com"
       )
       
       # Bridge WebRTC audio to SIP audio
       bridge_audio_streams(webrtc_session, sip_call)
       
       # Handle signaling (answer, hangup, etc.)
       handle_call_state_changes(sip_call)
   ```

#### Pros:
- ✅ FusionPBX already supports WebRTC
- ✅ Uses existing infrastructure
- ✅ No additional servers needed

#### Cons:
- ❌ Requires significant development work
- ❌ Complex media handling
- ❌ Need to handle codec negotiation

---

### Option 2: Use Janus Gateway (Media Server)

Janus Gateway can bridge WebRTC to SIP.

#### Architecture:
```
WebRTC Client (Browser)
    ↓ WebRTC
Janus Gateway (Media Server)
    ↓ SIP
FusionPBX → Extension 2001
```

#### Requirements:

1. **Install Janus Gateway:**
   ```bash
   # Install Janus with SIP plugin
   sudo apt-get install janus janus-plugin-sip
   ```

2. **Configure Janus SIP Plugin:**
   ```json
   {
     "sip": {
       "proxy": "136.115.41.45",
       "username": "webrtc-bridge",
       "password": "password"
     }
   }
   ```

3. **Implement Bridge Logic:**
   - Connect WebRTC client to Janus session
   - Use Janus API to create SIP call
   - Bridge the media streams

#### Pros:
- ✅ Production-ready solution
- ✅ Handles media transcoding
- ✅ Good documentation
- ✅ Scalable

#### Cons:
- ❌ Additional server component
- ❌ Requires configuration
- ❌ More complex architecture

---

### Option 3: Use Kurento Media Server

Similar to Janus but different technology stack.

#### Pros:
- ✅ Java-based (if your team prefers Java)
- ✅ Good WebRTC support

#### Cons:
- ❌ More resource-intensive
- ❌ Heavier than Janus

---

### Option 4: Twilio Voice SDK (SIP-Enabled)

If you want to leverage Twilio's infrastructure:

1. **Convert WebRTC call to Twilio call:**
   - Use Twilio Voice SDK to create a call from the browser
   - Then use existing Twilio → FusionPBX transfer flow

2. **Implementation:**
   ```javascript
   // In browser
   const call = device.connect({
       params: { extension: '2001' }
   });
   ```

#### Pros:
- ✅ Uses existing Twilio transfer infrastructure
- ✅ Less custom code needed
- ✅ Reliable infrastructure

#### Cons:
- ❌ Requires Twilio Voice SDK integration
- ❌ Additional Twilio costs
- ❌ Still not "direct" - goes through Twilio

---

## 🎯 Recommended Approach

For your use case, I recommend **Option 1 (FusionPBX WebRTC + Server-Side Bridge)** because:

1. ✅ **FusionPBX already supports WebRTC** - No additional servers needed
2. ✅ **Uses existing infrastructure** - You already have FusionPBX set up
3. ✅ **Direct transfer** - No intermediate services
4. ✅ **Cost-effective** - No additional service fees

## 📋 Implementation Steps (Option 1)

### Step 1: Enable FusionPBX WebRTC Profile

In FusionPBX:
1. Go to **Advanced → SIP Profiles**
2. Enable **wss** profile (WebSocket Secure)
3. Configure:
   - **WSS Port:** 7443
   - **External IP:** 136.115.41.45
   - **Codecs:** G722, PCMU, PCMA

### Step 2: Install Python SIP Library

```bash
pip install pjsua2
# or
pip install aiortc
# or
pip install python-sip
```

### Step 3: Implement Bridge Function

```python
# In webrtc_voice_server.py
import pjsua2 as pj

def bridge_webrtc_to_fusionpbx(webrtc_session_id, extension):
    """
    Bridge active WebRTC session to FusionPBX extension via SIP
    """
    freepbx_domain = os.getenv('FREEPBX_DOMAIN', '136.115.41.45')
    
    # Create SIP account and call
    # This is simplified - actual implementation would be more complex
    sip_uri = f"sip:{extension}@{freepbx_domain}"
    
    # Bridge WebRTC audio to SIP audio
    # Implementation details depend on chosen SIP library
    
    return sip_call_id
```

### Step 4: Update Transfer Handler

In `webrtc_voice_server.py`, replace the current transfer logic:

```python
# Current (sends instructions):
socketio.emit('transfer_initiated', {
    'instructions': transfer_instructions
})

# New (bridges directly):
bridge_webrtc_to_fusionpbx(session_id, target_extension)
socketio.emit('transfer_initiated', {
    'success': True,
    'extension': target_extension,
    'bridged': True,
    'message': 'Transferring now...'
})
```

## 🔧 Alternative: Quick Workaround

If you want a quick solution without full implementation:

### Use FusionPBX's WebRTC Client

1. **Configure FusionPBX WebRTC Extension:**
   - Create a WebRTC-enabled extension in FusionPBX
   - User can connect directly from browser

2. **Provide Direct WebRTC Link:**
   ```python
   # In transfer handler
   webrtc_url = f"https://136.115.41.45/app/calls/index.php?action=call&extension={extension}"
   socketio.emit('transfer_initiated', {
       'webrtc_url': webrtc_url,
       'message': 'Click to connect via WebRTC'
   })
   ```

3. **Browser redirects to FusionPBX WebRTC client**

This is not as seamless, but works with existing FusionPBX features.

## ✅ Summary

**Current State:**
- ❌ Direct transfer NOT implemented
- ✅ Transfer instructions are provided
- ✅ User must manually initiate transfer

**To Enable Direct Transfer:**
- ✅ Additional implementation required
- ✅ Recommend: FusionPBX WebRTC + Server-side SIP bridge
- ✅ Alternative: Use Janus Gateway or similar media server

**Quick Solution:**
- Provide FusionPBX WebRTC client link for direct connection

## 🎯 Next Steps

If you want to implement direct transfer, I can help with:

1. **Detailed implementation plan** for Option 1 (FusionPBX WebRTC bridge)
2. **Code examples** for SIP bridging
3. **FusionPBX WebRTC configuration** guide
4. **Testing strategy** for the bridge

Would you like me to proceed with implementing direct WebRTC-to-SIP bridging?
