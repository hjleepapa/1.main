# FusionPBX Call Transfer Setup Guide

## Problem
Call transfer from Twilio to FusionPBX fails with `status=failed`.

**Current Configuration:**
- FusionPBX Domain: `136.113.215.142`
- Extension: `2001`
- SIP URI: `sip:2001@136.113.215.142;transport=udp`

## Root Cause
Twilio cannot directly dial a SIP URI without proper configuration on the FusionPBX server. FusionPBX must be configured to:
1. Accept SIP calls from Twilio IP ranges
2. Allow SIP traffic through the firewall
3. Have the extension accessible

## Solution: Configure FusionPBX to Accept Twilio SIP Calls

### Step 1: Whitelist Twilio IP Ranges in FusionPBX

Twilio uses specific IP ranges for outbound SIP calls. You need to whitelist these in FusionPBX:

**Twilio IP Ranges:**
```
54.172.60.0/23
54.244.51.0/24
177.71.206.192/26
54.252.254.64/26
54.169.127.128/26
```

#### Option A: Configure via FusionPBX Web Interface

1. **Log into FusionPBX Admin Panel:**
   ```
   https://136.113.215.142
   ```

2. **Navigate to Firewall Settings:**
   ```
   Advanced → Firewall → Access Lists
   ```

3. **Create New Access List:**
   - Name: `Twilio-SIP`
   - Description: `Twilio SIP Trunk IP Ranges`
   - Add the IP ranges above

4. **Apply to SIP Context:**
   - Navigate to: `Advanced → SIP Profiles`
   - Edit your SIP profile
   - In "ACL" or "Permit" settings, add: `Twilio-SIP`

#### Option B: Configure via Asterisk Config Files (SSH)

1. **SSH into FusionPBX Server:**
   ```bash
   ssh root@136.113.215.142
   ```

2. **Edit PJSIP Config:**
   ```bash
   vi /etc/asterisk/pjsip.conf
   ```

3. **Add Twilio Endpoint Configuration:**
   ```ini
   [twilio-endpoint]
   type=endpoint
   context=from-trunk
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

4. **Create Context for Incoming Twilio Calls:**
   ```bash
   vi /etc/asterisk/extensions.conf
   ```
   
   Add or edit the `[from-trunk]` context:
   ```ini
   [from-trunk]
   exten => _X.,1,NoOp(Incoming SIP call from Twilio to extension ${EXTEN})
   exten => _X.,n,Goto(from-internal,${EXTEN},1)
   exten => _X.,n,Hangup()
   ```

5. **Reload Asterisk Configuration:**
   ```bash
   asterisk -rx "core reload"
   asterisk -rx "pjsip reload"
   ```

### Step 2: Configure Firewall to Allow SIP Traffic

**Open UDP Port 5060 for SIP:**
```bash
# On FusionPBX server
ufw allow 5060/udp
# OR
iptables -A INPUT -p udp --dport 5060 -j ACCEPT
```

**For WebRTC/SIP TLS (optional, port 5061):**
```bash
ufw allow 5061/tcp
```

### Step 3: Verify Extension 2001 Exists and Is Reachable

1. **Check Extension in FusionPBX:**
   ```
   Admin → Extensions → Check extension 2001 exists
   ```

2. **Verify Extension is Active:**
   - Extension must be registered (if using SIP phones)
   - Or extension must be assigned to a queue
   - Or extension must forward to another number

3. **Test Extension Manually:**
   - Use a SIP client (like Zoiper or Linphone)
   - Connect to: `sip:2001@136.113.215.142`
   - Verify you can reach the extension

### Step 4: Test SIP Connectivity from External IP

**From your local machine, test if FusionPBX accepts SIP:**
```bash
# Test SIP port
nc -zuv 136.113.215.142 5060

# Expected output:
# Connection to 136.113.215.142 5060 port [udp/sip] succeeded!
```

### Step 5: Configure SIP Authentication (Optional but Recommended)

If FusionPBX requires SIP authentication:

1. **Create SIP User for Twilio:**
   ```
   FusionPBX → Admin → Extensions → Add Extension
   ```
   - Extension: `9999` (or any unused number)
   - Secret: Generate strong password
   - Context: `from-trunk`

2. **Set Environment Variables:**
   ```bash
   FREEPBX_SIP_USERNAME=9999
   FREEPBX_SIP_PASSWORD=your_strong_password
   ```

3. **Update Transfer Code:**
   The code will automatically use SIP authentication if these variables are set.

### Step 6: Verify Transfer Works

1. **Make a test call via Twilio:**
   - Call your Twilio number
   - Say "transfer me to agent"
   - Check logs for detailed transfer status

2. **Check FusionPBX Logs:**
   ```bash
   ssh root@136.113.215.142
   tail -f /var/log/asterisk/full | grep "2001"
   ```

3. **Check Application Logs:**
   Look for:
   - `Transferring to SIP URI: sip:2001@136.113.215.142;transport=udp`
   - `Transfer callback for call ... status=completed` (success!)
   - Or error details if it fails

## Troubleshooting

### Transfer Still Fails?

1. **Check Application Logs for Error Details:**
   - Look for `❌ Transfer failed` messages
   - Check `Error Message` field
   - Review `Possible causes` list in logs

2. **Verify Twilio IP Ranges are Whitelisted:**
   ```bash
   # On FusionPBX server
   asterisk -rx "pjsip show endpoints" | grep twilio
   asterisk -rx "pjsip show identifies" | grep -A 5 twilio
   ```

3. **Check Firewall:**
   ```bash
   # On FusionPBX server
   ufw status | grep 5060
   iptables -L -n | grep 5060
   ```

4. **Test SIP Manually:**
   ```bash
   # From external machine
   sip-scan -s 136.113.215.142
   ```

5. **Check FusionPBX Asterisk Logs:**
   ```bash
   ssh root@136.113.215.142
   tail -100 /var/log/asterisk/full | grep -i "sip\|invite\|twilio"
   ```

## Expected Behavior After Configuration

When properly configured:

1. **Transfer Initiated:**
   ```
   Transferring to SIP URI: sip:2001@136.113.215.142;transport=udp
   ```

2. **Twilio Connects to FusionPBX:**
   - Twilio sends SIP INVITE to `136.113.215.142:5060`
   - FusionPBX accepts the call
   - Routes to extension 2001

3. **Transfer Success:**
   ```
   Transfer callback for call CA...: status=completed, extension=2001
   ✅ Transfer successful for call CA... to extension 2001
   ```

## Alternative: Use Twilio Elastic SIP Trunking

If direct SIP URI dialing doesn't work, you can set up Twilio Elastic SIP Trunking:

1. **Create SIP Trunk in Twilio Console:**
   - Navigate to: `Voice → Elastic SIP Trunking → Create Trunk`
   - Trunk Name: `FusionPBX-Trunk`

2. **Add Origination URI:**
   - URI: `sip:136.113.215.142`
   - Priority: 1
   - Weight: 1

3. **Add Termination URI:**
   - SIP URI: `136.113.215.142`
   - IP Access Control: Add FusionPBX IP

4. **Use Trunk in Transfer:**
   Update code to use trunk instead of direct SIP URI (requires code changes).

## Summary

**Required Configuration:**
1. ✅ Whitelist Twilio IP ranges in FusionPBX
2. ✅ Open UDP port 5060 in firewall
3. ✅ Verify extension 2001 exists and is reachable
4. ✅ (Optional) Configure SIP authentication if required

**Current Configuration:**
- FusionPBX Domain: `136.113.215.142`
- Extension: `2001`
- SIP URI Format: `sip:2001@136.113.215.142;transport=udp`
