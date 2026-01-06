# PSTN to SIP Conversion Architecture

## The Problem

When someone calls a regular phone number (DID), it's a **PSTN (Public Switched Telephone Network)** call. Your FusionPBX speaks **SIP (Session Initiation Protocol)**. You need a component to convert between these two protocols.

---

## Architecture Options

### Option 1: SIP Trunk Provider (Recommended - Easiest)

**How it works:**
- SIP trunk provider (Flowroute, Telnyx, VoIP.ms, etc.) receives PSTN calls to your DID
- Provider automatically converts PSTN → SIP
- Provider sends SIP call directly to your FusionPBX

```
PSTN Call → SIP Trunk Provider → SIP → FusionPBX → Your App
```

**Components:**
- **DID Provider**: Owns the phone number, receives PSTN calls
- **SIP Trunk**: Provider's service that converts PSTN to SIP
- **FusionPBX**: Receives SIP calls directly

**Configuration:**
```
FusionPBX Trunk Configuration:
- Provider: Flowroute (or Telnyx, VoIP.ms, etc.)
- SIP Server: sip.flowroute.com
- Username: Your trunk username
- Password: Your trunk password
- Register: Yes
```

**Pros:**
- ✅ Simplest setup - no additional hardware
- ✅ Provider handles PSTN ↔ SIP conversion
- ✅ Direct SIP connection to FusionPBX
- ✅ Usually cheaper than SBC solution
- ✅ Cloud-based, no on-premise equipment

**Cons:**
- ⚠️ Dependent on provider's infrastructure
- ⚠️ Less control over call routing

**Example Providers:**
- **Flowroute**: $0.99/month per DID + usage
- **Telnyx**: $0.35/month per DID + usage
- **VoIP.ms**: $0.85/month per DID + usage
- **Bandwidth**: Enterprise pricing

---

### Option 2: Session Border Controller (SBC) - Enterprise Solution

**How it works:**
- SBC sits at the edge of your network
- Receives PSTN calls (via T1/E1, PRI, or SIP trunk from carrier)
- Converts PSTN → SIP internally
- Routes SIP calls to FusionPBX

```
PSTN Call → Carrier → SBC → SIP → FusionPBX → Your App
```

**Components:**
- **Carrier**: Provides PSTN connectivity (T1/E1, PRI, or SIP trunk)
- **SBC**: Hardware/software that converts protocols and handles security
- **FusionPBX**: Receives SIP from SBC

**SBC Functions:**
1. **Protocol Conversion**: PSTN (TDM) ↔ SIP
2. **NAT Traversal**: Handles firewall/NAT issues
3. **Security**: Firewall, DoS protection, encryption
4. **Media Handling**: RTP proxy, transcoding
5. **Call Routing**: Routes calls based on rules
6. **Monitoring**: Call quality, statistics

**Popular SBC Options:**

#### A. Software SBC (Open Source)
- **FreeSWITCH**: Can act as SBC (you already have this!)
- **Asterisk**: Can act as SBC
- **Kamailio/OpenSIPS**: Lightweight SIP proxy/SBC
- **SIPwise SBC**: Commercial open-source

#### B. Commercial SBC
- **Audiocodes**: Mediant series
- **Ribbon Communications**: SBC 5000 series
- **Cisco**: Unified Border Element (CUBE)
- **Oracle**: Enterprise Session Border Controller

#### C. Cloud SBC
- **Twilio Elastic SIP Trunking**: Acts as SBC in cloud
- **Telnyx**: Cloud SBC functionality
- **Bandwidth**: Cloud SBC services

**Pros:**
- ✅ Full control over call routing
- ✅ Enhanced security features
- ✅ Better for high-volume deployments
- ✅ Can handle multiple carriers
- ✅ Advanced features (transcoding, recording, etc.)

**Cons:**
- ⚠️ More complex setup
- ⚠️ Higher cost (hardware or licensing)
- ⚠️ Requires expertise to configure
- ⚠️ Additional point of failure

---

### Option 3: FreeSWITCH as SBC (Your Current Infrastructure!)

**Great news:** You already have FreeSWITCH (via FusionPBX)! FreeSWITCH can act as an SBC.

**Architecture:**
```
PSTN Call → SIP Trunk Provider → FreeSWITCH (SBC Mode) → FusionPBX → Your App
```

**How to Configure:**

#### Step 1: Configure External SIP Profile in FusionPBX

FreeSWITCH can receive SIP calls from providers directly:

```xml
<!-- /etc/freeswitch/sip_profiles/external.xml -->
<profile name="external">
  <settings>
    <param name="sip-ip" value="136.115.41.45"/>
    <param name="sip-port" value="5060"/>
    <param name="rtp-ip" value="136.115.41.45"/>
    <param name="rtp-port-min" value="16384"/>
    <param name="rtp-port-max" value="32768"/>
    <param name="sip-trace" value="true"/>
    <param name="sip-capture" value="true"/>
  </settings>
  
  <!-- Gateway to SIP trunk provider -->
  <gateway name="flowroute">
    <param name="username" value="your_trunk_username"/>
    <param name="realm" value="sip.flowroute.com"/>
    <param name="password" value="your_trunk_password"/>
    <param name="register" value="true"/>
    <param name="register-proxy" value="sip.flowroute.com"/>
  </gateway>
</profile>
```

#### Step 2: Configure Inbound Route

Route incoming calls from trunk to your application:

```xml
<!-- FusionPBX Dialplan -->
<extension name="voice_assistant_inbound">
  <condition field="destination_number" expression="^YOUR_DID_NUMBER$">
    <action application="answer"/>
    <action application="lua" data="voice_assistant.lua"/>
    <!-- Or use mod_event_socket to send to your Python app -->
  </condition>
</extension>
```

#### Step 3: Use FreeSWITCH ESL for Call Control

Your Python app connects to FreeSWITCH via ESL:

```python
import freeswitchESL

# Connect to FreeSWITCH
con = freeswitchESL.ESLconnection("127.0.0.1", "8021", "ClueCon")

# Handle inbound call
def handle_inbound_call(call_uuid, caller_id, destination):
    # Answer call
    con.execute("answer", "", call_uuid)
    
    # Process with your voice assistant
    # ...
```

**Benefits:**
- ✅ No additional hardware needed
- ✅ FreeSWITCH already installed
- ✅ Full control over call handling
- ✅ Can integrate directly with your app

---

## Detailed Comparison

### SIP Trunk Provider vs SBC

| Feature | SIP Trunk Provider | SBC (Hardware/Software) |
|---------|-------------------|-------------------------|
| **Setup Complexity** | Low | Medium to High |
| **Cost** | $1-5/month + usage | $500-5000+ (hardware) or free (software) |
| **Control** | Limited | Full |
| **Security** | Provider handles | You control |
| **Scalability** | Provider scales | You scale |
| **Maintenance** | Provider maintains | You maintain |
| **Best For** | Small to medium deployments | Enterprise, high-volume |

---

## Recommended Architecture for Your Use Case

### For Your Current Setup:

**Recommended: SIP Trunk Provider + FreeSWITCH**

```
┌─────────────┐
│   PSTN       │
│   Caller     │
└──────┬───────┘
       │
       │ PSTN
       ▼
┌─────────────────┐
│  SIP Trunk      │  ← Flowroute, Telnyx, VoIP.ms
│  Provider       │     (Converts PSTN → SIP)
└──────┬──────────┘
       │
       │ SIP
       ▼
┌─────────────────┐
│  FreeSWITCH     │  ← Your FusionPBX
│  (SBC Mode)     │     (Receives SIP, routes calls)
└──────┬──────────┘
       │
       │ ESL/HTTP
       ▼
┌─────────────────┐
│  Your Python    │  ← Voice Assistant App
│  Application    │     (Processes calls)
└─────────────────┘
```

### Why This Works:

1. **SIP Trunk Provider** handles PSTN → SIP conversion (no hardware needed)
2. **FreeSWITCH** (already installed) acts as SBC/router
3. **Your Python app** receives call events via ESL
4. **No additional components** needed!

---

## Implementation Steps

### Step 1: Choose SIP Trunk Provider

**Recommended: Flowroute or Telnyx**

**Flowroute Setup:**
1. Sign up at flowroute.com
2. Purchase DID number
3. Get trunk credentials:
   - SIP Server: `sip.flowroute.com`
   - Username: Your trunk username
   - Password: Your trunk password

**Telnyx Setup:**
1. Sign up at telnyx.com
2. Purchase DID number
3. Create SIP connection
4. Get credentials

### Step 2: Configure FusionPBX Trunk

**Via FusionPBX GUI:**
1. Go to: `Advanced → Gateways → Add`
2. Gateway Name: `flowroute` (or provider name)
3. Gateway Profile: `external`
4. Username: Your trunk username
5. Password: Your trunk password
6. Proxy: `sip.flowroute.com` (or provider SIP server)
7. Register: `true`
8. Save

**Or via CLI:**
```bash
fs_cli -x "sofia profile external restart"
```

### Step 3: Configure Inbound Route

**Via FusionPBX GUI:**
1. Go to: `Dialplan → Inbound Routes → Add`
2. Destination Number: Your DID number (e.g., `+1234567890`)
3. Action: `Lua` or `Event Socket`
4. Script/Application: Route to your voice assistant

**Or create dialplan:**
```xml
<extension name="voice_assistant">
  <condition field="destination_number" expression="^\+?1234567890$">
    <action application="answer"/>
    <action application="set" data="api_hangup_hook=lua voice_assistant.lua"/>
    <action application="lua" data="voice_assistant.lua"/>
  </condition>
</extension>
```

### Step 4: Connect Your Python App

**Option A: FreeSWITCH ESL (Event Socket Library)**
```python
import freeswitchESL

# Connect to FreeSWITCH
con = freeswitchESL.ESLconnection("127.0.0.1", "8021", "ClueCon")

# Subscribe to events
con.events("plain", "CHANNEL_CREATE CHANNEL_ANSWER CHANNEL_HANGUP")

# Handle events
while True:
    e = con.recvEvent()
    if e:
        event_name = e.getHeader("Event-Name")
        if event_name == "CHANNEL_CREATE":
            call_uuid = e.getHeader("Unique-ID")
            caller_id = e.getHeader("Caller-Caller-ID-Number")
            # Process call
```

**Option B: mod_http (HTTP Callbacks)**
```python
# FreeSWITCH sends HTTP POST to your app
@app.route('/freeswitch/call', methods=['POST'])
def handle_freeswitch_call():
    call_uuid = request.form.get('Caller-Unique-ID')
    caller_id = request.form.get('Caller-Caller-ID-Number')
    # Process call
```

---

## Answer to Your Questions

### Q1: "Do we need a component to convert DID PSTN to SIP?"

**Answer:** Yes, but you have two options:

1. **SIP Trunk Provider** (easiest): Provider does the conversion automatically
   - You configure FusionPBX to receive SIP from provider
   - Provider handles PSTN → SIP conversion
   - No additional component needed on your side

2. **SBC** (more control): You handle the conversion
   - SBC receives PSTN (via T1/E1/PRI or SIP trunk)
   - SBC converts to SIP
   - SBC sends SIP to FusionPBX

### Q2: "Can SBC map to FusionPBX?"

**Answer:** Yes! SBC can absolutely map to FusionPBX:

**SBC Functions:**
- Receives calls (PSTN or SIP)
- Converts protocols if needed
- Routes calls to FusionPBX via SIP
- Handles security, NAT, media

**In your case:**
- **FreeSWITCH (already installed)** can act as SBC
- Or use a **SIP Trunk Provider** which acts as cloud SBC
- Or deploy a **dedicated SBC** (hardware or software)

---

## Cost Analysis

### Option 1: SIP Trunk Provider
- DID: $1-5/month
- Usage: $0.01-0.02/minute
- **Total for 1000 min/month**: ~$15-25/month

### Option 2: SBC Hardware
- Hardware: $500-5000 (one-time)
- Carrier T1/PRI: $200-500/month
- **Total**: High upfront, ongoing carrier costs

### Option 3: FreeSWITCH as SBC + SIP Trunk
- FreeSWITCH: Free (already have it)
- SIP Trunk: $1-5/month + usage
- **Total for 1000 min/month**: ~$15-25/month
- **Best value!**

---

## Recommendation

**For your use case, I recommend:**

1. **Use a SIP Trunk Provider** (Flowroute or Telnyx)
   - Simplest setup
   - No additional hardware
   - Provider handles PSTN → SIP conversion
   - Direct SIP connection to your FusionPBX

2. **Use FreeSWITCH (already installed) as your SBC/router**
   - Receives SIP calls from provider
   - Routes to your Python application
   - Handles call control via ESL

3. **No need for separate SBC hardware**
   - FreeSWITCH can handle SBC functions
   - Unless you need enterprise-grade features

**This gives you:**
- ✅ PSTN → SIP conversion (via provider)
- ✅ Call routing (via FreeSWITCH)
- ✅ Full control (via your Python app)
- ✅ Low cost (~$15-25/month for moderate usage)
- ✅ No additional hardware

---

## Next Steps

1. **Sign up with SIP trunk provider** (Flowroute or Telnyx)
2. **Purchase DID number**
3. **Configure trunk in FusionPBX**
4. **Set up inbound route** to your voice assistant
5. **Test with a real phone call**

Would you like me to create a step-by-step configuration guide for a specific provider?

