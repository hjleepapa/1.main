# Transfer Fix Summary

## 🔴 Problem
Your call transfer is failing with error: **"I'm sorry, the transfer failed."**

## 🎯 Root Cause
Simple SIP URI format (`sip:2000@34.26.59.14`) doesn't work without proper Twilio ↔ FreePBX connectivity.

## ✅ Two Solutions

### **Solution A: Trunk Number Method** ⭐ RECOMMENDED (Easiest)

Route calls through your Twilio trunk number back to FreePBX.

#### Configuration:

**1. Update `.env` file:**
```bash
# Add these lines
USE_TRUNK_NUMBER_TRANSFER=true
TWILIO_TRUNK_NUMBER=+19256337818
TWILIO_INBOUND_NUMBER=+12344007818
FREEPBX_DOMAIN=34.26.59.14
TRANSFER_TIMEOUT=30
```

**2. Configure FreePBX Inbound Route:**
```
Log into FreePBX Admin Panel
→ Connectivity 
→ Inbound Routes 
→ Add Inbound Route

Settings:
  DID Number: +19256337818
  Description: Twilio AI Transfer Route
  Set Destination: Queues → 2000 (or Extensions → 2000)

Save & Apply Config
```

**3. Restart your application**

**4. Test:** Call your number and say "transfer me to an agent"

#### Result TwiML:
```xml
<Response>
    <Say>Transferring you to an agent. Please wait.</Say>
    <Dial answerOnBridge="true" timeout="30">
        <Number>+19256337818</Number>
    </Dial>
</Response>
```

---

### **Solution B: SIP Trunk Method** (More Complex)

Direct SIP connection between Twilio and FreePBX.

#### Configuration:

**1. Configure Twilio Elastic SIP Trunk:**
```
Twilio Console → Voice → Elastic SIP Trunking → Create Trunk

Trunk Name: FreePBX-Trunk

Origination Tab:
  Add URI: sip:34.26.59.14
  Priority: 1
  Enabled: ✓

Termination Tab:
  Add your FreePBX IP to allowed list

Numbers Tab:
  Assign: +12344007818, +19256337818
```

**2. Configure FreePBX SIP Trunk:**
```
FreePBX → Connectivity → Trunks → Add SIP (chan_pjsip) Trunk

General:
  Trunk Name: Twilio
  Outbound CallerID: +19256337818

pjsip Settings:
  SIP Server: sip.twilio.com
  Context: from-trunk

Advanced:
  Match (Permit): Add Twilio IPs:
    54.172.60.0/23
    54.244.51.0/24
    177.71.206.192/26
    54.252.254.64/26
    54.169.127.128/26
```

**3. Update `.env`:**
```bash
USE_TRUNK_NUMBER_TRANSFER=false  # or leave unset
FREEPBX_DOMAIN=34.26.59.14
```

**4. Test the transfer**

#### Result TwiML:
```xml
<Response>
    <Say>Transferring you to an agent. Please wait.</Say>
    <Dial answerOnBridge="true" timeout="30">
        <Sip>sip:2000@34.26.59.14;transport=udp</Sip>
    </Dial>
</Response>
```

---

## 🔍 Verify Extension 2000 Exists

Before testing, ensure extension/queue 2000 is configured:

### Option 1: Queue (Recommended for call centers)
```
FreePBX → Applications → Queues → Add Queue

Queue Number: 2000
Queue Name: Support Queue
Ring Strategy: ringall
Static Agents: [Add your agents]
```

### Option 2: Extension
```
FreePBX → Applications → Extensions → Add Extension

Extension: 2000
Display Name: Support Agent
```

---

## 🧪 Testing

### Test 1: Direct Extension Call
```bash
# From any phone, call FreePBX and dial extension 2000
# This should work before testing transfer
```

### Test 2: Transfer Endpoint
```bash
curl -X POST https://hjlees.com/sambanova_todo/twilio/transfer \
  -d "extension=2000" \
  -d "CallSid=test" \
  -d "From=+1234567890"

# Should return valid TwiML XML
```

### Test 3: Voice Call Transfer
```
1. Call +12344007818 (your inbound number)
2. Enter PIN
3. Say: "Transfer me to an agent"
4. Should hear: "Transferring you to an agent. Please wait."
5. Call should connect to extension 2000
```

---

## 📊 What Changed in Code

### Enhanced Transfer Endpoint
- ✅ Added two transfer methods (trunk number vs SIP URI)
- ✅ Added `answer_on_bridge=True` to wait for agent answer
- ✅ Added transfer timeout configuration
- ✅ Added caller ID preservation
- ✅ Added transfer callback handler
- ✅ Added detailed logging

### New Transfer Callback
- ✅ Handles transfer success/failure
- ✅ Provides user-friendly error messages
- ✅ Logs transfer status for debugging

### Configuration Options
- ✅ `USE_TRUNK_NUMBER_TRANSFER`: Choose transfer method
- ✅ `TRANSFER_TIMEOUT`: Configure wait time
- ✅ `FREEPBX_SIP_USERNAME/PASSWORD`: Optional auth

---

## 📝 Environment Variables

Required in your `.env` file:

```bash
# === REQUIRED ===
FREEPBX_DOMAIN=34.26.59.14
TWILIO_TRUNK_NUMBER=+19256337818

# === TRANSFER METHOD ===
# Choose one:
USE_TRUNK_NUMBER_TRANSFER=true   # Easy method (recommended)
# OR
USE_TRUNK_NUMBER_TRANSFER=false  # SIP trunk method (requires setup)

# === OPTIONAL ===
TRANSFER_TIMEOUT=30
TWILIO_INBOUND_NUMBER=+12344007818
FREEPBX_SIP_USERNAME=            # Only if FreePBX requires auth
FREEPBX_SIP_PASSWORD=            # Only if FreePBX requires auth
```

---

## 🚨 Troubleshooting

### If Transfer Still Fails:

1. **Check logs:**
   ```bash
   # Look for these lines
   grep "Transferring call" logs/*.log
   grep "Transfer TwiML" logs/*.log
   grep "Transfer callback" logs/*.log
   ```

2. **Check FreePBX logs:**
   ```bash
   ssh user@34.26.59.14
   tail -f /var/log/asterisk/full | grep 2000
   ```

3. **Check Twilio debugger:**
   ```
   Twilio Console → Monitor → Logs → Errors
   Filter by your Call SID
   ```

4. **Verify firewall:**
   ```bash
   # On FreePBX server
   sudo iptables -L -n | grep 5060
   ```

### Common Error Messages:

| Error | Cause | Fix |
|-------|-------|-----|
| "Transfer failed" | Can't reach FreePBX | Check firewall, verify IP |
| "Agent is busy" | Extension busy | Wait or use queue |
| "Agent did not answer" | Timeout reached | Increase timeout or check extension |
| "Could not be completed" | SIP/config error | Review trunk setup |

---

## 📚 Documentation Files

- **Setup Guide**: `TWILIO_FREEPBX_SETUP.md` - Complete setup instructions
- **Troubleshooting**: `TRANSFER_TROUBLESHOOTING.md` - Debug checklist
- **Quick Start**: `CALL_TRANSFER_QUICKSTART.md` - 5-minute setup
- **Config Example**: `call_transfer_config.example.env` - All env vars

---

## ⚡ Quick Start (5 Minutes)

```bash
# 1. Add to .env
echo "USE_TRUNK_NUMBER_TRANSFER=true" >> .env
echo "TWILIO_TRUNK_NUMBER=+19256337818" >> .env
echo "FREEPBX_DOMAIN=34.26.59.14" >> .env

# 2. Configure FreePBX inbound route (via web UI)
#    DID: +19256337818 → Queue 2000

# 3. Restart application
python app.py

# 4. Test call
# Call +12344007818 and say "transfer me"
```

---

## 🎉 Expected Success

When working correctly, you'll see:

**Application Logs:**
```
Transferring call CA123... from +1234... to extension 2000
Using trunk number transfer to +19256337818
Transfer TwiML generated for call CA123...
Transfer callback for call CA123...: status=completed
✅ Transfer successful for call CA123... to extension 2000
```

**User Experience:**
```
User: "Transfer me to an agent"
AI: "Transferring you to an agent. Please wait."
[Call connects to extension 2000]
Agent: "Hello, how can I help you?"
```

---

## 💡 Recommendation

**Start with Solution A** (Trunk Number Method):
- ✅ Easier to configure
- ✅ Uses familiar phone number routing
- ✅ No SIP trunk configuration needed
- ✅ Works with standard FreePBX setup

**Upgrade to Solution B later** if you need:
- Direct SIP integration
- Lower latency
- More control over routing

---

## ✉️ Need Help?

If you're still having issues after trying Solution A, provide:
1. Application logs (grep "Transfer")
2. FreePBX logs (/var/log/asterisk/full)
3. Twilio debugger output
4. Your `.env` configuration (redacted)

Good luck! 🚀

