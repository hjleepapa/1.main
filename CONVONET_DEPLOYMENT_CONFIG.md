# Convonet Project Deployment Configuration Guide
## WebRTC Call Transfer, Call-Center Dashboard, Twilio, and Voice Assistant Setup

This comprehensive guide covers all configuration steps needed to deploy the Convonet project with WebRTC call transfer functionality, call-center agent dashboard, Twilio integration, and voice assistant capabilities.

---

## Table of Contents

1. [Overview](#overview)
2. [FusionPBX Configuration on Google Cloud](#fusionpbx-configuration-on-google-cloud)
3. [Twilio Configuration](#twilio-configuration)
4. [Call-Center Agent Dashboard Setup](#call-center-agent-dashboard-setup)
5. [Voice Assistant (WebRTC) Configuration](#voice-assistant-webrtc-configuration)
6. [Environment Variables](#environment-variables)
7. [Deployment to Render.com](#deployment-to-rendercom)
8. [Testing and Verification](#testing-and-verification)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### Architecture Flow

```mermaid
graph LR
    subgraph "User Browser"
        UA[User Browser<br/>Voice Assistant UI]
    end
    
    subgraph "Render.com"
        WS[WebSocket Server<br/>Socket.IO]
        WVS[WebRTC Voice Server]
        LG[LangGraph<br/>AI Orchestration]
    end
    
    subgraph "External Services"
        DEEP[Deepgram STT]
        OPENAI[OpenAI LLM/TTS]
        TWILIO[Twilio API]
    end
    
    subgraph "FusionPBX GCloud"
        FUSION[FusionPBX<br/>Extension 2001]
        AGENT[Agent Dashboard<br/>JsSIP Client]
    end
    
    UA -->|WebRTC Voice| WS
    WS -->|Audio Stream| WVS
    WVS -->|Transcribe| DEEP
    DEEP -->|Text| LG
    LG -->|Process| OPENAI
    OPENAI -->|Response| LG
    LG -->|Audio| UA
    
    UA -->|Transfer Request| WS
    WS -->|Initiate Transfer| TWILIO
    TWILIO -->|SIP INVITE| FUSION
    FUSION -->|Ring Extension| AGENT
    AGENT -->|Answer| FUSION
    FUSION -->|Bridge| TWILIO
    TWILIO -->|Bridged Audio| UA
    TWILIO -->|Bridged Audio| AGENT
```

For detailed flow diagrams with all components, see [WEBRTC_CALL_FLOW_DIAGRAM.md](./WEBRTC_CALL_FLOW_DIAGRAM.md)

### Components

1. **FusionPBX on Google Cloud**: PBX system for call handling and agent extensions
2. **Twilio**: Cloud communications platform for SIP trunking and call routing
3. **Call-Center Agent Dashboard**: Browser-based SIP client for agents
4. **WebRTC Voice Assistant**: AI-powered voice interface for users
5. **Render.com**: Hosting platform for the Flask application

---

## FusionPBX Configuration on Google Cloud

### Prerequisites

- Google Cloud Platform (GCP) account
- FusionPBX instance deployed on GCP Compute Engine
- Static external IP address for FusionPBX
- Domain name (optional but recommended)

### Step 1: Google Cloud Network Configuration

#### 1.1 Configure Firewall Rules

```bash
# SSH into GCP instance
gcloud compute ssh fusionpbx-instance --zone=us-central1-a

# Create firewall rule for SIP
gcloud compute firewall-rules create allow-sip \
    --allow udp:5060 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow SIP traffic"

# Create firewall rule for RTP (media)
gcloud compute firewall-rules create allow-rtp \
    --allow udp:10000:20000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow RTP media traffic"

# Create firewall rule for WebRTC (WSS)
gcloud compute firewall-rules create allow-webrtc \
    --allow tcp:7443 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow WebRTC WebSocket Secure"
```

#### 1.2 Configure Static External IP

```bash
# Reserve static IP address
gcloud compute addresses create fusionpbx-static-ip \
    --region=us-central1

# Get the IP address
gcloud compute addresses describe fusionpbx-static-ip \
    --region=us-central1

# Example output: 136.115.41.45
```

#### 1.3 Assign Static IP to Instance

```bash
# Stop the instance
gcloud compute instances stop fusionpbx-instance --zone=us-central1-a

# Assign the static IP
gcloud compute instances delete-access-config fusionpbx-instance \
    --access-config-name="External NAT" \
    --zone=us-central1-a

gcloud compute instances add-access-config fusionpbx-instance \
    --access-config-name="External NAT" \
    --address=136.115.41.45 \
    --zone=us-central1-a

# Start the instance
gcloud compute instances start fusionpbx-instance --zone=us-central1-a
```

### Step 2: FusionPBX System Configuration

#### 2.1 Configure NAT Settings

```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# Edit FreeSWITCH SIP profile
vi /etc/freeswitch/sip_profiles/external.xml

# Update NAT settings (find <param name="ext-sip-ip">)
<param name="sip-ip" value="10.128.0.8"/>              <!-- Internal IP -->
<param name="ext-sip-ip" value="136.115.41.45"/>       <!-- External IP -->
<param name="rtp-ip" value="10.128.0.8"/>              <!-- Internal IP -->
<param name="ext-rtp-ip" value="136.115.41.45"/>       <!-- External IP -->
<param name="sip-force-contact" value="external"/>     <!-- Force external contact -->
<param name="rtp-force-contact" value="external"/>     <!-- Force external RTP -->

# Save and reload
systemctl reload freeswitch
```

#### 2.2 Configure WebRTC Profile (for Agent Dashboard)

```bash
# Edit WebRTC profile
vi /etc/freeswitch/sip_profiles/internal-webrtc.xml

# Ensure these settings:
<param name="ws-binding" value=":7443"/>
<param name="wss-binding" value=":7443"/>
<param name="tls-binding" value=":7443"/>

# Reload configuration
fs_cli -x "reload mod_sofia"
```

#### 2.3 Configure SIP Authentication for Twilio

```bash
# Edit pjsip.conf
vi /etc/asterisk/pjsip.conf

# Add Twilio endpoint configuration
[twilio-endpoint]
type=endpoint
context=from-trunk
disallow=all
allow=ulaw
allow=alaw
direct_media=no
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
send_rpid=yes

[twilio-aor]
type=aor
contact=sip:twilio@127.0.0.1

[twilio-identify]
type=identify
endpoint=twilio-endpoint
match=54.172.60.0/23
match=54.244.51.0/24
match=177.71.206.192/26
match=54.252.254.64/26
match=54.169.127.128/26

# Reload Asterisk
asterisk -rx "core reload"
asterisk -rx "pjsip reload"
```

#### 2.4 Create Extension Context for Twilio Calls

```bash
# Edit extensions_custom.conf
vi /etc/asterisk/extensions_custom.conf

# Add context for incoming Twilio calls
[from-trunk]
exten => _X.,1,NoOp(Incoming call from Twilio to ${EXTEN})
exten => _X.,n,Goto(from-internal,${EXTEN},1)
exten => _X.,n,Hangup()

# Reload dialplan
asterisk -rx "dialplan reload"
```

### Step 3: Create Agent Extension

#### 3.1 Via FusionPBX Web Interface

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Create Extension:**
   ```
   Admin → Extensions → Add Extension
   ```
   - **Extension**: `2001` (or your preferred number)
   - **Display Name**: `Agent 2001`
   - **Password**: `[Generate strong password]`
   - **Caller ID**: `Agent 2001 <2001>`
   - **Context**: `from-internal`
   - **Transport**: `udp,tcp,wss` (enable WebRTC support)

3. **Enable WebRTC:**
   - Check "Enable WebRTC"
   - Port: `7443`
   - Protocol: `wss`

4. **Save and Apply Configuration**

#### 3.2 Via Command Line (Alternative)

```bash
# Create extension using FusionPBX CLI
cd /var/www/fusionpbx
php /var/www/fusionpbx/core/install/install.php \
    --type extension \
    --extension 2001 \
    --password [your_password] \
    --display_name "Agent 2001"
```

### Step 4: Configure STUN/TURN Server (for NAT traversal)

#### 4.1 Install and Configure CoTurn

```bash
# Install CoTurn
apt-get update
apt-get install coturn

# Configure CoTurn
vi /etc/turnserver.conf

# Add configuration:
listening-port=3478
tls-listening-port=5349
listening-ip=10.128.0.8
external-ip=136.115.41.45
realm=136.115.41.45
server-name=136.115.41.45

# Static auth user (for agents)
user=agent:P@ssw0rd
user=agent2:P@ssw0rd2

# Start CoTurn
systemctl enable coturn
systemctl start coturn
```

#### 4.2 Update FusionPBX Firewall for TURN

```bash
# Allow TURN ports
ufw allow 3478/udp
ufw allow 3478/tcp
ufw allow 5349/tcp
ufw allow 49152:65535/udp  # TURN relay ports
```

### Step 5: Verify FusionPBX Configuration

```bash
# Check SIP status
fs_cli -x "sofia status"

# Check extensions
fs_cli -x "user_exists id 2001"

# Test WebRTC profile
fs_cli -x "sofia status profile internal-webrtc"

# Check pjsip endpoints
asterisk -rx "pjsip show endpoints"
asterisk -rx "pjsip show identifies"
```

---

## Twilio Configuration

### Step 1: Create Twilio Account and Get Credentials

1. **Sign up for Twilio:**
   - Go to https://www.twilio.com/
   - Create account and verify phone number
   - Get Account SID and Auth Token from Dashboard

2. **Purchase Phone Numbers:**
   - Purchase an inbound number (e.g., `+1234567890`)
   - Optionally purchase a trunk number for SIP (e.g., `+1098765432`)

### Step 2: Configure Twilio Elastic SIP Trunking

#### 2.1 Create SIP Trunk

1. **Go to Twilio Console:**
   ```
   Voice → Elastic SIP Trunking → Create New Trunk
   ```

2. **Configure Trunk:**
   - **Trunk Name**: `FusionPBX-Trunk`
   - **Origination SIP URI**: `sip:136.115.41.45`
   - **Priority**: `1`
   - **Weight**: `1`
   - **Enabled**: ✓

3. **Add Termination (if bidirectional needed):**
   - Add FusionPBX IP: `136.115.41.45`
   - Allow IP: ✓

4. **Assign Phone Numbers:**
   - Add inbound number: `+1234567890`
   - Add trunk number (if purchased): `+1098765432`

### Step 3: Configure Twilio Webhook

#### 3.1 Set Voice Webhook URL

1. **Go to Phone Numbers:**
   ```
   Phone Numbers → Manage → Active Numbers → [Your Number]
   ```

2. **Configure Voice & Fax:**
   - **A CALL COMES IN**: Webhook
   - **URL**: `https://hjlees.com/convonet_todo/twilio/voice`
   - **HTTP Method**: `POST`

3. **Save Configuration**

### Step 4: Whitelist Twilio IPs in FusionPBX

Twilio uses specific IP ranges for outbound SIP calls. These should already be configured in Step 2.3, but verify:

```bash
# Verify IP whitelist in pjsip.conf
grep -A 10 "twilio-identify" /etc/asterisk/pjsip.conf

# Should include:
# match=54.172.60.0/23
# match=54.244.51.0/24
# match=177.71.206.192/26
# match=54.252.254.64/26
# match=54.169.127.128/26
```

---

## Call-Center Agent Dashboard Setup

### Step 1: Configure Call Center Application

#### 1.1 Update SIP Configuration

Edit `call_center/config.py`:

```python
SIP_CONFIG = {
    'domain': '136.115.41.45',  # FusionPBX domain/IP
    'wss_port': 7443,           # WebSocket Secure port
    'transport': 'wss',         # Use WSS for secure WebSocket
    
    # STUN/TURN servers for NAT traversal
    'ice_servers': [
        {
            'urls': 'stun:136.115.41.45:3478'  # Your STUN server
        },
        {
            'urls': [
                'turn:136.115.41.45:3478?transport=udp'
            ],
            'username': 'agent',
            'credential': 'P@ssw0rd'  # Match CoTurn configuration
        }
    ]
}
```

#### 1.2 Database Setup

```bash
# Run database initialization
cd /path/to/project
python call_center/init_db.py
```

This creates:
- `cc_agents` table
- `cc_calls` table
- `cc_agent_activities` table

#### 1.3 Create Agent Accounts

```bash
# Via Python script
python -c "
from call_center.models import Agent, db
from app import create_app

app = create_app()
with app.app_context():
    agent = Agent(
        username='agent2001',
        email='agent2001@example.com',
        extension='2001',
        sip_username='2001',
        sip_password='[FusionPBX extension password]',
        status='Offline'
    )
    db.session.add(agent)
    db.session.commit()
    print('Agent created:', agent.username)
"
```

### Step 2: Configure Frontend SIP Client

The call center dashboard uses JsSIP library for SIP communication. Configuration is in `call_center/static/js/call_center.js`.

Key settings (already configured):
- **WebSocket URL**: `wss://136.115.41.45:7443`
- **SIP URI**: `sip:2001@136.115.41.45`
- **ICE Servers**: Configured with STUN/TURN

### Step 3: Test Agent Dashboard

1. **Access Dashboard:**
   ```
   https://hjlees.com/call_center/
   ```

2. **Login:**
   - Username: `agent2001`
   - Password: `[Your password]`
   - SIP Username: `2001`
   - SIP Password: `[FusionPBX extension password]`
   - Domain: `136.115.41.45`

3. **Verify Connection:**
   - Status should show "Connected" (green)
   - SIP registration should show "Registered"

---

## Voice Assistant (WebRTC) Configuration

### Step 1: Configure Deepgram (Speech-to-Text)

#### 1.1 Get Deepgram API Key

1. **Sign up for Deepgram:**
   - Go to https://www.deepgram.com/
   - Create account and get API key

2. **Set Environment Variable:**
   ```bash
   DEEPGRAM_API_KEY=dg_your_api_key_here
   ```

#### 1.2 Verify Deepgram Integration

The code in `deepgram_webrtc_integration.py` is already configured. Test:

```bash
# Test Deepgram service
python -c "
from deepgram_service import get_deepgram_service
service = get_deepgram_service()
print('Deepgram service:', service.get_service_info())
"
```

### Step 2: Configure Redis (Session Management)

#### 2.1 Setup Redis

```bash
# If using Redis Cloud or similar
# Get connection details from your Redis provider
```

#### 2.2 Environment Variables

```bash
REDIS_HOST=your-redis-host.com
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
```

### Step 3: Configure OpenAI (for TTS/Whisper)

The voice assistant uses:
- **Whisper API**: For transcription (if Deepgram unavailable)
- **TTS API**: For text-to-speech responses

```bash
OPENAI_API_KEY=sk-your-openai-api-key
```

### Step 4: Configure Voice PIN Authentication

#### 4.1 Set Voice PIN for Users

```sql
-- Update user voice PIN
UPDATE users_convonet 
SET voice_pin = '1234'  -- Use strong PIN in production
WHERE id = '[user_id]';
```

#### 4.2 Enable/Disable Test PIN (Optional)

```bash
# Enable test PIN for development (default: disabled)
ENABLE_TEST_PIN=true
TEST_VOICE_PIN=1234
```

### Step 5: Test WebRTC Voice Assistant

1. **Access Voice Assistant:**
   ```
   https://hjlees.com/convonet_todo/webrtc/voice-assistant
   ```

2. **Enter PIN:**
   - Enter your voice PIN
   - Click "Authenticate"

3. **Start Conversation:**
   - Click "Start Recording"
   - Speak your request
   - Click "Stop Recording"
   - Wait for AI response

---

## Environment Variables

### Complete Environment Variable List

Create a `.env` file or set these in Render.com:

```bash
# ===== FLASK CORE =====
FLASK_KEY=your-secret-key-here
DB_URI=postgresql://user:password@host:5432/dbname

# ===== OPENAI =====
OPENAI_API_KEY=sk-your-openai-api-key

# ===== GOOGLE OAUTH =====
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH2_TOKEN_B64=base64-encoded-credentials

# ===== REDIS =====
REDIS_HOST=your-redis-host.com
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# ===== COMPOSIO =====
COMPOSIO_API_KEY=ak_test_placeholder
COMPOSIO_PROJECT_ID=pr_test_placeholder

# ===== TWILIO =====
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_TRUNK_NUMBER=+1098765432  # Optional, for SIP trunking

# ===== WEBHOOK URLS =====
WEBHOOK_BASE_URL=https://hjlees.com
WEBSOCKET_BASE_URL=wss://hjlees.com/convonet_todo/ws

# ===== FUSIONPBX =====
FREEPBX_DOMAIN=136.115.41.45
FREEPBX_SIP_USERNAME=  # Optional, leave empty for IP-based auth
FREEPBX_SIP_PASSWORD=  # Optional, leave empty for IP-based auth

# ===== CALL TRANSFER =====
TRANSFER_TIMEOUT=30
SUPPORT_EXTENSION=2000
SALES_EXTENSION=2000
GENERAL_EXTENSION=2000
OPERATOR_EXTENSION=2000

# ===== DEEPGRAM =====
DEEPGRAM_API_KEY=dg_your_deepgram_api_key

# ===== VOICE PIN =====
ENABLE_TEST_PIN=false  # Set to true for development only
TEST_VOICE_PIN=1234    # Only used if ENABLE_TEST_PIN=true

# ===== RATE LIMITING =====
RATELIMIT_STORAGE_URL=redis://your-redis-url
RATELIMIT_DEFAULT=10 per minute

# ===== SENTRY (Optional) =====
SENTRY_DSN=https://your-sentry-dsn@o123456.ingest.sentry.io/123456
```

---

## Deployment to Render.com

### Step 1: Create Render Service

1. **Go to Render Dashboard:**
   - https://dashboard.render.com/

2. **Create New Web Service:**
   - Connect your Git repository
   - Select branch: `main`

### Step 2: Configure Build Settings

#### 2.1 Build Command

```bash
pip install -r requirements.txt
```

#### 2.2 Start Command

```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT passenger_wsgi:application
```

### Step 3: Set Environment Variables

In Render Dashboard → Environment:

1. **Add all variables from the Environment Variables section above**
2. **Use "Sync" for sensitive values** (they won't be displayed)
3. **Set public values directly** (e.g., `FREEPBX_DOMAIN`, `COMPOSIO_API_KEY`)

### Step 4: Configure Health Check

- **Health Check Path**: `/`
- **Health Check Interval**: `30 seconds`

### Step 5: Deploy

1. **Save configuration**
2. **Render will automatically build and deploy**
3. **Monitor build logs for any errors**
4. **Once deployed, your service will be available at:**
   ```
   https://hjlees.com
   ```

---

## Testing and Verification

### Step 1: Test FusionPBX Connectivity

```bash
# Test SIP port from external machine
nc -zuv 136.115.41.45 5060

# Test WebRTC port
nc -zuv 136.115.41.45 7443

# Test STUN/TURN
nc -zuv 136.115.41.45 3478
```

### Step 2: Test Twilio Webhook

```bash
# Test webhook endpoint
curl -X POST https://hjlees.com/convonet_todo/twilio/voice \
  -d "CallSid=test123" \
  -d "From=+15555555555" \
  -d "To=+1234567890"

# Should return TwiML response
```

### Step 3: Test Call Transfer

1. **Call Twilio number**: `+1234567890`
2. **Follow voice prompts**
3. **Say "transfer me to an agent"**
4. **Verify:**
   - Call should transfer to FusionPBX extension 2001
   - Agent dashboard should show incoming call
   - Agent can answer and talk

### Step 4: Test WebRTC Voice Assistant

1. **Open**: `https://hjlees.com/convonet_todo/webrtc/voice-assistant`
2. **Enter PIN**: Your configured voice PIN
3. **Test conversation**:
   - "Create a todo item"
   - "What are my tasks?"
   - "Transfer me to an agent"

### Step 5: Test Agent Dashboard

1. **Open**: `https://hjlees.com/call_center/`
2. **Login**: Use agent credentials
3. **Verify SIP connection**: Should show "Connected" and "Registered"
4. **Test incoming call**: Have someone call and transfer to extension 2001
5. **Test outbound call**: Use dialpad to make a call

---

## Troubleshooting

### Issue: Call Transfer Fails

**Symptoms:**
- "Transfer failed" message
- Call doesn't reach FusionPBX
- Agent doesn't receive call

**Solutions:**

1. **Check Twilio Logs:**
   ```
   Twilio Console → Monitor → Logs → Calls
   ```
   - Look for SIP errors
   - Check call status

2. **Check FusionPBX Logs:**
   ```bash
   ssh root@136.115.41.45
   tail -f /var/log/asterisk/full | grep "2001"
   ```

3. **Verify SIP Connectivity:**
   ```bash
   # From external machine
   sip-scan -s 136.115.41.45
   ```

4. **Check Firewall:**
   ```bash
   # On FusionPBX
   ufw status
   iptables -L -n | grep 5060
   ```

5. **Verify Extension Exists:**
   ```bash
   asterisk -rx "core show channels"
   asterisk -rx "sip show peers" | grep 2001
   ```

### Issue: Agent Dashboard Can't Connect

**Symptoms:**
- SIP status shows "Disconnected"
- Registration fails
- "Connection timeout" error

**Solutions:**

1. **Check WebSocket Port:**
   ```bash
   # Verify port 7443 is open
   netstat -tlnp | grep 7443
   ```

2. **Check FusionPBX WebRTC Profile:**
   ```bash
   fs_cli -x "sofia status profile internal-webrtc"
   ```

3. **Verify Credentials:**
   - Double-check extension number and password
   - Ensure extension exists in FusionPBX

4. **Check Browser Console:**
   - Open browser DevTools (F12)
   - Look for WebSocket connection errors
   - Check JsSIP debug messages

5. **Test STUN/TURN:**
   ```bash
   # Test STUN server
   stun-client 136.115.41.45:3478
   ```

### Issue: WebRTC Voice Assistant Not Working

**Symptoms:**
- Audio not recording
- Transcription fails
- No AI response

**Solutions:**

1. **Check Deepgram API Key:**
   ```bash
   # Verify environment variable is set
   echo $DEEPGRAM_API_KEY
   ```

2. **Check Browser Permissions:**
   - Allow microphone access when prompted
   - Check browser settings for microphone permissions

3. **Check Redis Connection:**
   ```bash
   # Test Redis connectivity
   python -c "
   from convonet.redis_manager import redis_manager
   print('Redis available:', redis_manager.is_available())
   "
   ```

4. **Check WebSocket Connection:**
   - Open browser DevTools → Network
   - Look for WebSocket connection
   - Check for connection errors

5. **Verify PIN:**
   ```sql
   -- Check user voice PIN
   SELECT id, username, voice_pin 
   FROM users_convonet 
   WHERE id = '[user_id]';
   ```

### Issue: No Audio During Call

**Symptoms:**
- Call connects but no audio
- One-way audio
- Static/noise

**Solutions:**

1. **Check RTP Ports:**
   ```bash
   # Verify RTP ports are open
   ufw status | grep 10000
   ```

2. **Check Codec Compatibility:**
   - Ensure both sides support: `ulaw`, `alaw`
   - Check FusionPBX codec settings

3. **Check NAT Configuration:**
   ```bash
   # Verify NAT settings in FusionPBX
   grep -i "ext-sip-ip\|ext-rtp-ip" /etc/freeswitch/sip_profiles/external.xml
   ```

4. **Check TURN Server:**
   - Verify CoTurn is running
   - Test TURN connectivity
   - Check credentials

### Issue: High Latency or Poor Audio Quality

**Solutions:**

1. **Use Deepgram (instead of Whisper):**
   - Deepgram has lower latency
   - Better real-time performance

2. **Optimize Codec:**
   - Use `Opus` for WebRTC (better quality)
   - Use `ulaw/alaw` for SIP (compatibility)

3. **Check Network:**
   - Monitor bandwidth usage
   - Check for packet loss
   - Optimize server location

---

## Additional Resources

### Documentation Links

- **FusionPBX Documentation**: https://docs.fusionpbx.com/
- **Twilio Documentation**: https://www.twilio.com/docs
- **Deepgram Documentation**: https://developers.deepgram.com/
- **JsSIP Documentation**: https://jssip.net/
- **FreeSWITCH Documentation**: https://freeswitch.org/confluence/

### Support Channels

- **FusionPBX Community**: https://community.freepbx.org/
- **Twilio Support**: https://support.twilio.com/
- **Render Support**: https://render.com/docs

### Configuration Files Reference

- **FusionPBX**: `/etc/freeswitch/`
- **Asterisk**: `/etc/asterisk/`
- **Call Center**: `call_center/config.py`
- **Environment**: `.env` or Render Dashboard

---

## Quick Reference Checklist

### Pre-Deployment

- [ ] FusionPBX deployed on GCP with static IP
- [ ] Firewall rules configured (SIP, RTP, WebRTC)
- [ ] NAT settings configured in FusionPBX
- [ ] Twilio account created and configured
- [ ] SIP trunk configured in Twilio
- [ ] FusionPBX extension created (2001)
- [ ] STUN/TURN server configured
- [ ] Redis instance configured
- [ ] Deepgram API key obtained
- [ ] All environment variables set

### Deployment

- [ ] Render.com service created
- [ ] Build command configured
- [ ] Start command configured
- [ ] All environment variables added to Render
- [ ] Health check configured
- [ ] Service deployed successfully

### Post-Deployment Testing

- [ ] FusionPBX SIP connectivity verified
- [ ] Twilio webhook tested
- [ ] Call transfer tested
- [ ] Agent dashboard connection verified
- [ ] WebRTC voice assistant tested
- [ ] End-to-end call flow tested

---

## Conclusion

This guide provides comprehensive configuration for deploying the Convonet project with WebRTC call transfer, call-center dashboard, Twilio integration, and voice assistant capabilities. Follow each section carefully and verify each step before proceeding to the next.

For issues not covered in this guide, refer to the Troubleshooting section or consult the documentation links provided.

---

**Last Updated**: 2024-11-16  
**Project**: Convonet Team Collaboration System  
**Version**: 1.0

