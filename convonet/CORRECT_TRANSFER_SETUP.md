# Correct Call Transfer Setup - Voice AI → FreePBX

## The Correct Flow

```
1. User calls +12344007818 (Twilio inbound number)
2. Twilio → Voice AI (Convonet assistant answers)
3. Voice AI chats with user
4. User says "transfer me to an agent"
5. Voice AI issues transfer command
6. Twilio dials FreePBX extension 2000
7. Agent answers, call is bridged
```

## Why Transfer Is Failing

When your code tries to execute:
```xml
<Dial><Sip>sip:2000@34.26.59.14</Sip></Dial>
```

Twilio needs **outbound SIP connectivity** to reach your FreePBX server at `34.26.59.14`.

## The Real Solution: Configure SIP Interface for Twilio

### Option 1: Use Twilio's SIP Interface (Recommended)

Twilio needs to be able to make **outbound SIP calls** to your FreePBX.

#### Step 1: Enable Twilio SIP Connectivity

Twilio can make SIP calls, but you need to ensure your FreePBX accepts them.

**In FreePBX, configure to accept SIP from Twilio IPs:**

```
FreePBX → Connectivity → Firewall → Advanced Settings

Add Twilio IP ranges to "Permit" list:
54.172.60.0/23
54.244.51.0/24
177.71.206.192/26
54.252.254.64/26
54.169.127.128/26
```

#### Step 2: Create Anonymous SIP Context (FreePBX)

FreePBX needs to accept anonymous/unauthenticated SIP calls from Twilio:

```bash
# SSH into FreePBX
ssh root@34.26.59.14

# Edit pjsip.conf
vi /etc/asterisk/pjsip.conf

# Add this section:
[twilio-endpoint]
type=endpoint
context=from-twilio
disallow=all
allow=ulaw
allow=alaw
direct_media=no
rtp_symmetric=yes

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
```

#### Step 3: Create Custom Context for Twilio Calls

```bash
# Edit extensions_custom.conf
vi /etc/asterisk/extensions_custom.conf

# Add this context:
[from-twilio]
exten => _X.,1,NoOp(Incoming call from Twilio to ${EXTEN})
exten => _X.,n,Goto(from-internal,${EXTEN},1)
```

#### Step 4: Restart Asterisk

```bash
asterisk -rx "core reload"
```

#### Step 5: Test

Your TwiML will now work:
```xml
<Response>
    <Say>Transferring you to an agent. Please wait.</Say>
    <Dial answerOnBridge="true" timeout="30">
        <Sip>sip:2000@34.26.59.14</Sip>
    </Dial>
</Response>
```

---

### Option 2: Use Twilio Elastic SIP Trunking (More Robust)

This creates a proper SIP trunk between Twilio and FreePBX.

#### Step 1: Create Elastic SIP Trunk in Twilio

```
Twilio Console → Voice → Elastic SIP Trunking → Create New Trunk

Trunk Name: FreePBX-Production

Origination Tab → Add Origination URI:
  URI: sip:34.26.59.14
  Priority: 1
  Weight: 1
  Enabled: ✓

Termination Tab → Add Termination URI:
  SIP URI: 34.26.59.14
  
Termination Tab → IP Access Control Lists:
  Create ACL with FreePBX IP: 34.26.59.14
```

#### Step 2: Configure FreePBX to Accept Twilio Trunk

```
FreePBX → Connectivity → Trunks → Add SIP (chan_pjsip) Trunk

General Tab:
  Trunk Name: Twilio-Trunk
  Outbound CallerID: (leave default)

pjsip Settings Tab:
  SIP Server: (leave empty - this is for outbound)
  Context: from-trunk
  
pjsip Settings → Advanced:
  Match (Permit):
    54.172.60.0/23
    54.244.51.0/24
    177.71.206.192/26
    54.252.254.64/26
    54.169.127.128/26
```

#### Step 3: Update Your Code to Use Trunk

Since you have SIP trunk, you can use the simple SIP URI format:

```python
# Your current code should work:
sip_uri = f"sip:{extension}@{freepbx_domain}"
dial.sip(sip_uri)
```

---

### Option 3: Use Twilio's SIP Registration (If FreePBX Requires Auth)

If your FreePBX requires SIP authentication:

#### Step 1: Create SIP User in FreePBX

```
FreePBX → Connectivity → Extensions → Add SIP Extension

Extension: 9999 (use a special extension for Twilio)
Display Name: Twilio Transfer
Secret: [generate strong password]
```

#### Step 2: Add Credentials to Your .env

```bash
FREEPBX_SIP_USERNAME=9999
FREEPBX_SIP_PASSWORD=your_strong_password
```

#### Step 3: Updated Code (Already Supported)

Your code already supports this:
```python
dial.sip(
    sip_uri,
    username=os.getenv('FREEPBX_SIP_USERNAME', ''),
    password=os.getenv('FREEPBX_SIP_PASSWORD', '')
)
```

---

## Quick Test: Is FreePBX Reachable?

### Test 1: Network Connectivity

```bash
# From Twilio's perspective, test if FreePBX is reachable
# Use a SIP tester tool or:

ping 34.26.59.14
telnet 34.26.59.14 5060
```

### Test 2: FreePBX SIP Status

```bash
# SSH into FreePBX
ssh root@34.26.59.14

# Check if SIP is listening
asterisk -rx "pjsip show endpoints"
netstat -tulpn | grep 5060

# Check firewall
iptables -L -n | grep 5060
```

### Test 3: Manual SIP Call

Use a SIP client (like Zoiper) to manually dial:
```
sip:2000@34.26.59.14
```

If this works, your FreePBX is configured correctly.

---

## Environment Configuration

Update your `.env` with:

```bash
# FreePBX Configuration
FREEPBX_DOMAIN=34.26.59.14
TRANSFER_TIMEOUT=30

# Optional: If FreePBX requires SIP authentication
FREEPBX_SIP_USERNAME=9999
FREEPBX_SIP_PASSWORD=your_password

# These are NOT needed for correct flow:
# USE_TRUNK_NUMBER_TRANSFER=false  # Don't use this
# TWILIO_TRUNK_NUMBER=              # Not needed for AI→FreePBX transfer
```

---

## What NOT to Do

❌ **Don't create an inbound route for your trunk number pointing to extension 2000**
   - This would bypass the Voice AI entirely
   - User would go directly to FreePBX, skipping conversation

❌ **Don't dial the trunk number in the transfer**
   - `<Number>+19256337818</Number>` would create a loop
   - This is for inbound calls, not transfers

✅ **Do use direct SIP URI to FreePBX:**
   - `<Sip>sip:2000@34.26.59.14</Sip>`
   - This maintains the correct flow: AI first, then transfer

---

## Debugging Transfer Failures

### Check 1: FreePBX Logs

```bash
# Watch for incoming SIP INVITE from Twilio
tail -f /var/log/asterisk/full | grep "INVITE"

# Look for:
# - SIP INVITE sip:2000@34.26.59.14
# - From: Twilio IP addresses
# - Any authentication errors
```

### Check 2: Firewall Rules

```bash
# Ensure Twilio can reach FreePBX
sudo iptables -L -n -v | grep 5060

# Temporarily disable for testing:
sudo iptables -F
sudo systemctl stop fail2ban
```

### Check 3: FreePBX Extension Status

```bash
# Check if extension 2000 is registered
asterisk -rx "pjsip show endpoints" | grep 2000

# Or for queues:
asterisk -rx "queue show 2000"
```

### Check 4: Application Logs

Look for:
```
Transferring to SIP URI: sip:2000@34.26.59.14
Transfer TwiML generated
```

### Check 5: Twilio Debugger

```
Twilio Console → Monitor → Logs → Debugger
Filter by CallSid
Look for SIP errors or "Unable to route" messages
```

---

## Expected Working TwiML

When configured correctly, your transfer endpoint will generate:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Amy">Transferring you to an agent. Please wait.</Say>
    <Dial answerOnBridge="true" timeout="30" callerId="+1234567890" 
          action="/convonet_todo/twilio/transfer_callback?extension=2000">
        <Sip>sip:2000@34.26.59.14</Sip>
    </Dial>
    <Say voice="Polly.Amy">I'm sorry, the transfer failed. Please try again later.</Say>
    <Hangup/>
</Response>
```

Twilio will:
1. Make SIP call to `sip:2000@34.26.59.14`
2. Wait for agent to answer (`answerOnBridge="true"`)
3. Bridge the call
4. Call `/transfer_callback` with status

---

## Success Checklist

- [ ] FreePBX firewall allows Twilio IPs (54.172.60.0/23, etc.)
- [ ] Port 5060 (UDP) is open and accessible
- [ ] Extension/queue 2000 exists in FreePBX
- [ ] FreePBX accepts anonymous SIP or you configured auth
- [ ] Can manually dial sip:2000@34.26.59.14 from SIP client
- [ ] Application logs show "Transferring to SIP URI"
- [ ] Twilio debugger shows SIP INVITE being sent
- [ ] FreePBX logs show incoming INVITE from Twilio IP

---

## Most Likely Issue

**Firewall blocking Twilio → FreePBX SIP traffic**

Quick fix:
```bash
# On FreePBX server, temporarily allow all SIP:
sudo iptables -I INPUT -p udp --dport 5060 -j ACCEPT
sudo iptables -I INPUT -p udp --dport 10000:20000 -j ACCEPT  # RTP

# Test transfer
# If it works, add Twilio IPs permanently to firewall
```

---

## Next Steps

1. **Choose Option 1 (Simplest):** Configure FreePBX to accept SIP from Twilio IPs
2. **Test extension 2000** manually from a SIP phone
3. **Check firewall** rules on FreePBX
4. **Make test call** and try transfer
5. **Check logs** if it fails (FreePBX + Application + Twilio)

The code is now correct - the issue is FreePBX network/firewall configuration!

