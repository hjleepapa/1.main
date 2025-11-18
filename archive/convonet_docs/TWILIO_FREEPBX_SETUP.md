# Twilio to FreePBX Call Transfer Setup Guide

## Problem
Transfer fails with: "I'm sorry, the transfer failed. Please try again later."

## Root Cause
Twilio cannot directly dial `sip:2000@34.26.59.14` without proper SIP trunk configuration between Twilio and FreePBX.

## Solution: Configure Twilio Elastic SIP Trunking

### Step 1: FreePBX Configuration

#### 1.1 Create SIP Trunk for Twilio

**Go to FreePBX Admin Panel:**
```
Connectivity → Trunks → Add SIP (chan_pjsip) Trunk
```

**General Tab:**
- Trunk Name: `Twilio`
- Outbound CallerID: `+19256337818` (your Twilio trunk number)

**pjsip Settings Tab:**

**SIP Server:**
```
sip.twilio.com
```

**Context:** `from-trunk`

**Outbound Authentication:**
- Username: `(leave empty - IP authentication)`
- Secret: `(leave empty - IP authentication)`

**Registration:** `None`

**Advanced Tab:**

**Match (Permit):** Add Twilio's IP ranges:
```
54.172.60.0/23
54.244.51.0/24
177.71.206.192/26
54.252.254.64/26
54.169.127.128/26
```

**Codecs:**
- ulaw
- alaw

#### 1.2 Create Inbound Route

```
Connectivity → Inbound Routes → Add Inbound Route
```

- Description: `Twilio AI Transfer`
- DID Number: `+19256337818` (your trunk number)
- Set Destination: Your queue or extension `2000`

#### 1.3 Verify Queue/Extension 2000 Exists

```
Applications → Queues → Check queue 2000 exists
OR
Applications → Extensions → Check extension 2000 exists
```

### Step 2: Twilio Configuration

#### 2.1 Configure Elastic SIP Trunking

**Go to Twilio Console:**
```
Voice → Elastic SIP Trunking → Create New Trunk
```

**Trunk Name:** `FreePBX-Trunk`

#### 2.2 Add Origination URI

**Under "Origination":**
```
Origination SIP URI: sip:34.26.59.14
Priority: 1
Weight: 1
Enabled: ✓
```

**Add Authentication (if required):**
- Username: (if FreePBX requires auth)
- Password: (if FreePBX requires auth)

#### 2.3 Add Termination URI

**Under "Termination":**

Add your FreePBX public IP to allowed IPs:
```
SIP URI: sip:34.26.59.14
```

**Add Twilio IP addresses to FreePBX whitelist**

#### 2.4 Assign Phone Number

**Under "Numbers":**
- Add your inbound number: `+12344007818`
- Add your trunk number: `+19256337818`

### Step 3: Update Application Code

Now update the transfer endpoint to use the proper SIP format:

**Option A: Use SIP Domain (Recommended)**

Update `convonet/routes.py`:

```python
# Get SIP trunk domain from environment
sip_trunk_domain = os.getenv('TWILIO_SIP_TRUNK_DOMAIN', 'your-trunk.pstn.twilio.com')
freepbx_domain = os.getenv('FREEPBX_DOMAIN', '34.26.59.14')

# Use proper SIP URI format for Twilio trunk
sip_uri = f"sip:{extension}@{freepbx_domain};transport=udp"

# Create dial with proper parameters
dial = response.dial(
    answer_on_bridge=True,
    timeout=30,
    caller_id=request.form.get('From', '')
)
dial.sip(sip_uri)
```

**Option B: Use Number-based Transfer**

If you want to route through the trunk using a phone number:

```python
# Dial via Twilio trunk to FreePBX
# This assumes FreePBX trunk is configured to handle this number
dial = response.dial(
    answer_on_bridge=True,
    timeout=30,
    caller_id=request.form.get('From', '')
)

# Use the trunk number as routing
dial.number(
    f"+19256337818",  # Your Twilio trunk number
    status_callback_event="initiated ringing answered completed",
    status_callback=f"{webhook_base_url}/convonet_todo/twilio/transfer_status"
)
```

### Step 4: Test Configuration

#### Test 1: Test Twilio → FreePBX Connectivity

From Twilio Console, test the trunk:
```
Elastic SIP Trunking → Your Trunk → Test
```

#### Test 2: Direct SIP Call

Use a SIP client to test:
```
sip:2000@34.26.59.14
```

#### Test 3: Test via API

```bash
curl -X POST https://hjlees.com/convonet_todo/twilio/transfer \
  -d "extension=2000" \
  -d "CallSid=test" \
  -d "From=+1234567890"
```

### Step 5: Firewall Configuration

#### FreePBX Firewall

Allow Twilio IP ranges:
```bash
# Add to FreePBX firewall
54.172.60.0/23
54.244.51.0/24
177.71.206.192/26
54.252.254.64/26
54.169.127.128/26
```

#### Or disable firewall temporarily for testing:
```bash
sudo systemctl stop fail2ban
sudo iptables -F
```

### Troubleshooting

#### Issue: "Transfer failed"

**Check FreePBX logs:**
```bash
tail -f /var/log/asterisk/full
```

**Look for:**
- SIP INVITE from Twilio IPs
- Authentication failures
- Dial plan errors

#### Issue: Call connects but no audio

**Problem:** NAT or codec mismatch

**Solution:**
1. Configure STUN/TURN servers
2. Check codec compatibility (use ulaw/alaw)
3. Verify RTP port range is open (10000-20000)

#### Issue: Extension 2000 not found

**Check in FreePBX:**
```bash
asterisk -rx "queue show 2000"
# OR
asterisk -rx "database show"
```

### Environment Variables

Add to `.env`:
```bash
# FreePBX Configuration
FREEPBX_DOMAIN=34.26.59.14
FREEPBX_SIP_PORT=5060

# Twilio SIP Trunk
TWILIO_SIP_TRUNK_DOMAIN=your-trunk.pstn.twilio.com
TWILIO_TRUNK_NUMBER=+19256337818
TWILIO_INBOUND_NUMBER=+12344007818

# Transfer Settings
TRANSFER_TIMEOUT=30
TRANSFER_CALLER_ID_FORMAT=original  # original, trunk, or custom
```

## Alternative: Use Twilio Voice API for Transfer

If SIP trunk setup is too complex, use Twilio's REST API:

```python
from twilio.rest import Client

def transfer_via_api(call_sid, extension):
    client = Client(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN')
    )
    
    # Update the call to dial FreePBX
    call = client.calls(call_sid).update(
        url=f"{webhook_base_url}/convonet_todo/twilio/dial_freepbx?extension={extension}",
        method='POST'
    )
    
    return call

@convonet_todo_bp.route('/twilio/dial_freepbx', methods=['POST'])
def dial_freepbx():
    extension = request.args.get('extension', '2000')
    response = VoiceResponse()
    
    # Use conference or direct dial
    dial = response.dial(timeout=30, answer_on_bridge=True)
    dial.number(f"+19256337818")  # Route through trunk
    
    return Response(str(response), mimetype='text/xml')
```

## Recommended Configuration

For most reliable setup:

1. **Use IP Authentication** (no username/password)
2. **Whitelist Twilio IPs** in FreePBX
3. **Use `answer_on_bridge=True`** in Dial verb
4. **Set proper timeout** (30 seconds)
5. **Log everything** for debugging

## Next Steps

1. ✅ Configure FreePBX SIP trunk for Twilio
2. ✅ Configure Twilio Elastic SIP trunk
3. ✅ Update application code with proper SIP format
4. ✅ Test connectivity
5. ✅ Monitor logs and adjust

---

**Need Help?**
- FreePBX Community: https://community.freepbx.org/
- Twilio Support: https://support.twilio.com/
- SIP Debugging: Enable SIP debugging in FreePBX

