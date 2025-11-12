# Transfer Failed - Quick Troubleshooting Guide

## Your Current Issue

**Error:** Transfer fails and plays "I'm sorry, the transfer failed. Please try again later."

**Your Setup:**
- Inbound Number: `+12344007818`
- Trunk Number: `+19256337818`
- Target Extension: `2000`
- FreePBX IP: `34.26.59.14`

## Quick Fix Options

### Option 1: Use Trunk Number Method (Easiest)

This routes the call through your Twilio trunk number back to FreePBX.

**Step 1:** Add to `.env`:
```bash
USE_TRUNK_NUMBER_TRANSFER=true
TWILIO_TRUNK_NUMBER=+19256337818
```

**Step 2:** Configure FreePBX Inbound Route:
```
FreePBX → Connectivity → Inbound Routes → Add Route
DID Number: +19256337818
Set Destination: Queue 2000 (or Extension 2000)
```

**Step 3:** Test the call again

**Expected TwiML:**
```xml
<Response>
    <Say>Transferring you to an agent. Please wait.</Say>
    <Dial answerOnBridge="true" timeout="30" callerId="+1234567890">
        <Number>+19256337818</Number>
    </Dial>
</Response>
```

### Option 2: Configure SIP Trunk (More Complex)

This uses direct SIP connectivity between Twilio and FreePBX.

**Step 1:** Configure Twilio Elastic SIP Trunk
```
Twilio Console → Elastic SIP Trunking → Create Trunk
Origination URI: sip:34.26.59.14
```

**Step 2:** Configure FreePBX to Accept Twilio
```
FreePBX → Connectivity → Trunks → Add SIP Trunk
Trunk Name: Twilio
Outbound CallerID: +19256337818
Match (Permit): Add Twilio IPs
```

**Step 3:** Keep default setting:
```bash
USE_TRUNK_NUMBER_TRANSFER=false  # (or don't set it)
```

## Diagnostic Steps

### Check 1: Test FreePBX Extension

From a regular phone, call extension 2000 directly:
```
If it works: FreePBX extension is good ✅
If it fails: Fix extension/queue configuration ❌
```

### Check 2: Check FreePBX Logs

```bash
# SSH into FreePBX server
tail -f /var/log/asterisk/full | grep 2000

# Look for incoming SIP INVITE from Twilio IPs
# Twilio IPs: 54.172.60.0/23, 54.244.51.0/24, etc.
```

### Check 3: Test Transfer Endpoint

```bash
curl -X POST https://hjlees.com/convonet_todo/twilio/transfer \
  -d "extension=2000" \
  -d "CallSid=test123" \
  -d "From=+1234567890"

# Should return TwiML with <Dial> verb
```

### Check 4: Check Application Logs

Look for these log lines:
```
Transferring call CA... from +123... to extension 2000
Using SIP URI transfer to sip:2000@34.26.59.14;transport=udp
OR
Using trunk number transfer to +19256337818
```

## Common Issues & Solutions

### Issue 1: "Transfer failed" - Extension not reachable

**Cause:** FreePBX cannot be reached from Twilio

**Solutions:**
1. **Check firewall:** Allow Twilio IPs in FreePBX firewall
   ```bash
   # Temporarily disable for testing
   sudo systemctl stop fail2ban
   ```

2. **Check SIP port:** Ensure port 5060 (UDP) is open
   ```bash
   sudo netstat -tulpn | grep 5060
   ```

3. **Verify FreePBX is running:**
   ```bash
   sudo systemctl status asterisk
   ```

### Issue 2: "Transfer failed" - Authentication error

**Cause:** FreePBX requires SIP authentication

**Solution:** Add credentials to `.env`:
```bash
FREEPBX_SIP_USERNAME=your_sip_user
FREEPBX_SIP_PASSWORD=your_sip_pass
```

### Issue 3: Extension 2000 not found

**Cause:** Extension/queue doesn't exist

**Solution:** Create in FreePBX:
```
Applications → Queues → Add Queue
Queue Number: 2000
Queue Name: Support Queue
```

### Issue 4: Call connects but drops immediately

**Cause:** RTP/media path issue

**Solutions:**
1. Configure NAT settings in FreePBX
2. Use STUN server
3. Check RTP ports (10000-20000) are open

### Issue 5: Twilio shows error "Unable to create record"

**Cause:** Invalid SIP URI format

**Solution:** Check TwiML output matches:
```xml
<Dial>
    <Sip>sip:2000@34.26.59.14;transport=udp</Sip>
</Dial>
```

## Recommended Quick Fix

**For immediate testing, use Option 1 (Trunk Number Method):**

1. Add to `.env`:
   ```bash
   USE_TRUNK_NUMBER_TRANSFER=true
   TWILIO_TRUNK_NUMBER=+19256337818
   ```

2. In FreePBX, create inbound route:
   ```
   DID: +19256337818 → Queue 2000
   ```

3. Restart application

4. Make test call and say "transfer me"

This bypasses complex SIP trunk setup and uses regular phone number routing.

## Get Help

If still not working, collect these logs:

1. **Application logs:**
   ```bash
   # Check transfer TwiML output
   grep "Transfer TwiML" logs/app.log
   ```

2. **FreePBX logs:**
   ```bash
   tail -100 /var/log/asterisk/full
   ```

3. **Twilio debugger:**
   ```
   Twilio Console → Monitor → Debugger
   Filter by Call SID
   ```

Share these logs for further assistance.

## Testing Checklist

- [ ] Extension 2000 exists in FreePBX
- [ ] Extension 2000 answers when called directly
- [ ] Twilio Elastic SIP trunk is configured (if using SIP method)
- [ ] FreePBX firewall allows Twilio IPs
- [ ] Environment variables are set correctly
- [ ] Application has been restarted after config changes
- [ ] Transfer endpoint returns valid TwiML
- [ ] FreePBX logs show incoming call attempt
- [ ] Application logs show transfer initiation

## Expected Working Flow

```
1. User says "transfer me"
2. App redirects to /twilio/transfer?extension=2000
3. Transfer endpoint generates TwiML
4. Twilio sends call to FreePBX (via trunk or SIP)
5. FreePBX routes to extension/queue 2000
6. Agent answers
7. Call is bridged ✅
```

## Next Steps

1. Try **Option 1** (trunk number method) first
2. Check logs if it fails
3. Verify FreePBX inbound route exists
4. Test extension 2000 independently
5. Review full setup guide: `TWILIO_FREEPBX_SETUP.md`

