# WebRTC Voice Assistant → FusionPBX Direct Transfer Implementation

## Overview

This guide explains how to implement **direct WebRTC transfer** from the voice assistant (`https://hjlees.com/convonet_todo/webrtc/voice-assistant`) to FusionPBX extensions (e.g., `2001@136.115.41.45`) using the **same WSS profile** as the call center.

## Current Status

✅ **Task 1 (Call Center):** Fully implemented - agents connect directly via JsSIP  
⚠️ **Task 2 (Voice Assistant):** Shows transfer instructions only - needs implementation

## Architecture

Both tasks use the **same FusionPBX WSS profile** (`wss://136.115.41.45:7443`):

```
┌─────────────────────────────────────────────────────────────┐
│                  FusionPBX WSS Profile                      │
│              wss://136.115.41.45:7443                       │
│                                                             │
│  ┌─────────────────┐         ┌──────────────────┐         │
│  │  Task 1:        │         │  Task 2:         │         │
│  │  Call Center    │         │  Voice Assistant │         │
│  │  2005@...       │         │  2001@...        │         │
│  │  (Agent)        │         │  (Transfer)      │         │
│  └─────────────────┘         └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Approach

**Recommended:** Client-side JsSIP connection (same as call center)

When transfer is initiated:
1. ✅ User is already in a WebRTC session with the voice assistant
2. ✅ Client receives `transfer_initiated` event
3. ✅ **NEW:** Client creates a JsSIP connection to FusionPBX
4. ✅ Client places a call to the target extension
5. ✅ Bridge the two WebRTC sessions (voice assistant ↔ FusionPBX)

## Step-by-Step Implementation

### Step 1: Add JsSIP Library to Voice Assistant

The voice assistant already uses WebRTC for audio, but needs JsSIP for SIP signaling.

**Update `convonet/templates/webrtc_voice_assistant.html`:**

```html
<!-- Add JsSIP library (same as call center) -->
<script src="https://cdn.jsdelivr.net/npm/jssip@3.10.1/dist/jssip.min.js"></script>
```

### Step 2: Add SIP Configuration

Add FusionPBX WSS configuration to the template:

```html
<script>
    // FusionPBX WSS Configuration (same as call center)
    window.FUSIONPBX_CONFIG = {
        domain: '136.115.41.45',
        wss_port: 7443,
        transport: 'wss'
    };
</script>
```

### Step 3: Implement Transfer Handler

Update the `transfer_initiated` event handler to create a direct SIP call:

**In `webrtc_voice_assistant.html`:**

```javascript
let sipUserAgent = null;
let sipCall = null;
let transferInProgress = false;

socket.on('transfer_initiated', async (data) => {
    console.log('🔄 Transfer initiated:', data);
    
    if (data.success && !transferInProgress) {
        transferInProgress = true;
        
        // Show transfer status
        showStatus(`Connecting to ${data.department} (Extension ${data.extension})...`, 'info');
        
        try {
            // Initialize SIP connection to FusionPBX
            await initiateTransferCall(data.extension, data);
        } catch (error) {
            console.error('Transfer failed:', error);
            showStatus('Transfer failed. Please use manual options below.', 'error');
            transferInProgress = false;
        }
    }
});

async function initiateTransferCall(extension, transferData) {
    const config = window.FUSIONPBX_CONFIG;
    
    // Clean domain
    let cleanDomain = config.domain.trim();
    cleanDomain = cleanDomain.replace(/^wss?:\/\//, '');
    cleanDomain = cleanDomain.split(':')[0];
    
    // WebSocket URL
    const wsUrl = `wss://${cleanDomain}:${config.wss_port}`;
    console.log(`Connecting to FusionPBX: ${wsUrl}`);
    
    // Create WebSocket interface
    const socket = new JsSIP.WebSocketInterface(wsUrl);
    
    // Create SIP User Agent
    // Note: For transfer, we may not need full registration
    // But we'll use a temporary extension or anonymous connection
    const sipConfig = {
        sockets: [socket],
        uri: `sip:transfer@${cleanDomain}`, // Temporary/anonymous URI
        // No password needed if FusionPBX allows anonymous calls
        display_name: 'Voice Assistant Transfer',
        register: false, // Don't register, just make a call
        session_timers: false,
        use_preloaded_route: false
    };
    
    sipUserAgent = new JsSIP.UA(sipConfig);
    
    // Event handlers
    sipUserAgent.on('connected', () => {
        console.log('✓ Connected to FusionPBX');
        makeTransferCall(extension, cleanDomain);
    });
    
    sipUserAgent.on('disconnected', () => {
        console.log('✗ Disconnected from FusionPBX');
    });
    
    sipUserAgent.on('registrationFailed', (e) => {
        console.error('Registration failed (expected for anonymous):', e);
        // Still try to make call
        makeTransferCall(extension, cleanDomain);
    });
    
    // Start the UA
    sipUserAgent.start();
}

function makeTransferCall(extension, domain) {
    // Target URI
    const target = JsSIP.URI.parse(`sip:${extension}@${domain}`);
    
    // Create call options
    const options = {
        eventHandlers: {
            progress: (e) => {
                console.log('Call progressing...', e);
                showStatus('Calling extension ' + extension + '...', 'info');
            },
            failed: (e) => {
                console.error('Call failed:', e);
                showStatus('Call failed: ' + (e.cause || 'Unknown error'), 'error');
                transferInProgress = false;
                cleanupSIP();
            },
            ended: (e) => {
                console.log('Call ended:', e);
                showStatus('Call ended', 'info');
                transferInProgress = false;
                cleanupSIP();
            },
            confirmed: (e) => {
                console.log('Call confirmed (answered)');
                showStatus('Connected! Transfer complete.', 'success');
                // At this point, you may want to:
                // 1. Stop the voice assistant audio
                // 2. Bridge the audio streams
                // 3. Or just let both run simultaneously
            },
            peerconnection: (e) => {
                console.log('Peer connection created:', e);
                const pc = e.peerconnection;
                
                // Handle remote audio stream
                pc.addEventListener('track', (event) => {
                    const remoteAudio = new Audio();
                    remoteAudio.srcObject = event.streams[0];
                    remoteAudio.play().catch(err => {
                        console.error('Error playing remote audio:', err);
                    });
                    
                    // Add to page for user to hear
                    document.body.appendChild(remoteAudio);
                });
            }
        },
        mediaConstraints: {
            audio: true,
            video: false
        }
    };
    
    // Create and send INVITE
    sipCall = sipUserAgent.call(target, options);
    
    // Handle local stream (microphone)
    sipCall.on('peerconnection', (e) => {
        const pc = e.peerconnection;
        const localStream = pc.getLocalStreams()[0];
        if (localStream) {
            // Your existing microphone stream can be used here
            // Or create a new one
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    stream.getTracks().forEach(track => {
                        pc.addTrack(track, stream);
                    });
                });
        }
    });
}

function cleanupSIP() {
    if (sipCall) {
        sipCall.terminate();
        sipCall = null;
    }
    if (sipUserAgent) {
        sipUserAgent.stop();
        sipUserAgent = null;
    }
}
```

### Step 4: Alternative - Use Existing Extension Credentials

If FusionPBX requires authentication, you can use extension credentials:

```javascript
async function initiateTransferCall(extension, transferData) {
    // If you have extension credentials for transfers
    // (e.g., a dedicated "transfer" extension)
    const transferExtension = 'transfer'; // Or use existing extension
    const transferPassword = 'your_password';
    
    const sipConfig = {
        sockets: [socket],
        uri: `sip:${transferExtension}@${cleanDomain}`,
        password: transferPassword,
        display_name: 'Voice Assistant',
        register: true // Register this time
    };
    
    // ... rest of implementation
}
```

### Step 5: Update Server-Side Transfer Handler (Optional)

You can update `webrtc_voice_server.py` to indicate direct transfer is supported:

```python
socketio.emit('transfer_initiated', {
    'success': True,
    'extension': target_extension,
    'department': department,
    'direct_transfer': True,  # Indicate client can connect directly
    'fusionpbx_domain': freepbx_domain,
    'wss_port': 7443,
    'message': 'Connecting you directly to an agent...'
}, namespace='/voice', room=session_id)
```

## Testing

### Test 1: Basic Connection

1. Open voice assistant: `https://hjlees.com/convonet_todo/webrtc/voice-assistant`
2. Start a conversation
3. Say "transfer me to an agent" or "transfer me to extension 2001"
4. Check browser console for SIP connection logs
5. Verify call is placed to FusionPBX

### Test 2: Extension Answer

1. Ensure extension 2001 is registered in FusionPBX
2. Initiate transfer
3. Answer the call on extension 2001
4. Verify audio is working both ways

### Test 3: Call Center Integration

1. Have an agent logged into call center (`hjlees.com/call-center`)
2. Initiate transfer from voice assistant
3. Verify agent receives the call
4. Test full conversation flow

## Troubleshooting

### Issue: SIP Connection Fails

**Symptoms:** `WebSocket connection to 'wss://136.115.41.45:7443' failed`

**Solutions:**
1. ✅ Verify WSS profile is running: `fs_cli -x "sofia status profile wss"`
2. ✅ Check firewall allows port 7443
3. ✅ Verify WSS profile binds to `0.0.0.0:7443` (not internal IP)
4. ✅ Accept self-signed certificate in browser (if using)

### Issue: Call Fails with 403/401

**Symptoms:** Call rejected by FusionPBX

**Solutions:**
1. Check if extension exists: `fs_cli -x "user_exists id 2001 domain-name 136.115.41.45"`
2. Verify ACL allows connections: Check FusionPBX Access Control
3. Try with extension credentials instead of anonymous

### Issue: No Audio

**Symptoms:** Call connects but no audio

**Solutions:**
1. Check codec compatibility: Ensure G722, PCMU, or PCMA is enabled
2. Verify microphone permissions in browser
3. Check RTP ports are open (16384-32768 UDP)
4. Verify NAT traversal settings in FusionPBX

## Complete Integration Example

See `call_center/static/js/call_center.js` for a complete working example of:
- ✅ JsSIP initialization
- ✅ SIP registration
- ✅ Making calls
- ✅ Handling audio streams
- ✅ Call state management

You can adapt this code for the voice assistant transfer functionality.

## Summary

**Both Tasks Use Same Infrastructure:**
- ✅ Same FusionPBX WSS profile (`wss://136.115.41.45:7443`)
- ✅ Same JsSIP library
- ✅ Same connection method
- ✅ Different extensions (2005 vs 2001)

**Implementation:**
- ✅ Task 1: Already complete
- ✅ Task 2: Add JsSIP client to voice assistant (see code above)

**Once WSS profile is fixed (binding to 0.0.0.0):**
- ✅ Both tasks will work simultaneously
- ✅ No conflicts
- ✅ Shared infrastructure
