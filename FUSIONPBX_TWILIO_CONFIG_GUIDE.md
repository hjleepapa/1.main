# FusionPBX Configuration for Twilio Call Transfer

## Overview

This guide configures FusionPBX at **136.115.41.45** to accept SIP transfers from Twilio voice calls.

**Flow:**
```
Twilio Voice Call → AI Agent → Transfer to FusionPBX Extension 2001
```

## Required Configuration

### 1. Whitelist Twilio IP Ranges

Twilio uses these IP ranges for outbound SIP. Add them to FusionPBX firewall/ACL.

**Twilio IP Ranges:**
```
54.172.60.0/23
54.244.51.0/24
177.71.206.192/26
54.252.254.64/26
54.169.127.128/26
```

### Configuration Method A: Via FusionPBX Web GUI

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to Access Lists:**
   ```
   Advanced → Firewall → Access Lists
   ```

3. **Create New Access List:**
   - Name: `Twilio-SIP`
   - Add each IP range one by one:
     - `54.172.60.0/23`
     - `54.244.51.0/24`
     - `177.71.206.192/26`
     - `54.252.254.64/26`
     - `54.169.127.128/26`
   - Click "Save"

4. **Apply Access List to SIP Profile:**
   ```
   Advanced → SIP Profiles → [Your Profile]
   ```
   - Scroll to "Access Control"
   - Add "Twilio-SIP" to "Permit" list
   - Click "Save" and "Apply Config"

### Configuration Method B: Via SSH/Asterisk Config

1. **SSH into FusionPBX:**
   ```bash
   ssh root@136.115.41.45
   ```

2. **Edit PJSIP Config:**
   ```bash
   vi /etc/asterisk/pjsip.conf
   ```

3. **Add Twilio Endpoint:**
   ```ini
   [twilio-endpoint]
   type=endpoint
   context=from-twilio
   disallow=all
   allow=ulaw
   allow=alaw
   direct_media=no
   rtp_symmetric=yes
   force_rport=yes

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

4. **Create Dial Plan Context:**
   ```bash
   vi /etc/asterisk/extensions_custom.conf
   ```
   
   Add:
   ```ini
   [from-twilio]
   exten => _X.,1,NoOp(Incoming SIP call from Twilio to extension ${EXTEN})
   exten => _X.,n,Set(CHANNEL(language)=en)
   exten => _X.,n,Goto(from-internal,${EXTEN},1)
   exten => _X.,n,Hangup()
   ```

5. **Reload Asterisk:**
   ```bash
   asterisk -rx "core reload"
   asterisk -rx "pjsip reload"
   ```

### 2. Open Firewall Ports

#### On the VM/Server Level

**Open UDP 5060 for SIP:**
```bash
# Using ufw
ufw allow 5060/udp

# Using iptables
iptables -A INPUT -p udp --dport 5060 -j ACCEPT
iptables -A INPUT -p udp --dport 10000:20000 -j ACCEPT

# Save iptables rules
iptables-save > /etc/iptables/rules.v4
```

**Open RTP Ports 10000-20000:**
```bash
ufw allow 10000:20000/udp
```

#### If Using Cloud Provider (Google Cloud, AWS, etc.)

Create firewall rules to allow SIP traffic:

**Google Cloud:**
```bash
gcloud compute firewall-rules create allow-twilio-sip \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=udp:5060 \
    --source-ranges=54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26

gcloud compute firewall-rules create allow-twilio-rtp \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=udp:10000-20000 \
    --source-ranges=54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26
```

**AWS:**
```bash
# Create Security Group rules for SIP
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxx \
    --protocol udp \
    --port 5060 \
    --source-group sg-twilio
```

### 3. Verify Extension 2001 Exists

**Via FusionPBX Web GUI:**
1. Login to `https://136.115.41.45`
2. Go to: `Accounts → Extensions`
3. Search for extension `2001`
4. Verify:
   - Extension is active
   - Has a valid device/endpoint
   - Is assigned to a dial plan context

**Or check via SSH:**
```bash
asterisk -rx "pjsip list endpoints" | grep 2001
```

### 4. Test Configuration

#### Test 1: Verify SIP Port is Open

From your local machine:
```bash
nc -zuv 136.115.41.45 5060
```

**Expected:** `Connection to 136.115.41.45 5060 port [udp/sip] succeeded!`

#### Test 2: Check SIP Registration

```bash
asterisk -rx "pjsip show endpoints" | grep 2001
```

Should show extension 2001 as registered.

#### Test 3: Test Transfer from Twilio

Make a test call and request transfer to agent. Check logs:

```bash
# On FusionPBX
tail -f /var/log/asterisk/full

# Look for:
# - SIP INVITE from Twilio IP (54.172.x.x)
# - Extension 2001 ringing
# - Call connected
```

### 5. Monitor Transfer Logs

**Check Asterisk CLI for incoming calls:**
```bash
asterisk -rvvvvv
```

**Watch for:**
```
-- Executing [2001@from-twilio:1] NoOp("SIP/twilio-...", "Incoming SIP call from Twilio to extension 2001") in new stack
-- Executing [2001@from-twilio:2] Goto("SIP/twilio-...", "from-internal,2001,1") in new stack
-- Executing [2001@from-internal:1] Macro("SIP/2001-...", "user-callerid|SKIPTTL|SKIP") in new stack
```

### 6. Common Issues & Solutions

#### Issue: "SIP INVITE rejected" or "403 Forbidden"

**Cause:** Twilio IP not whitelisted or ACL blocking

**Solution:**
1. Verify Twilio IP ranges in ACL
2. Check SIP profile configuration
3. Reload Asterisk: `asterisk -rx "pjsip reload"`

#### Issue: "Extension not found" or "408 Request Timeout"

**Cause:** Extension 2001 doesn't exist or isn't registered

**Solution:**
1. Verify extension exists in FusionPBX
2. Check extension is active
3. Test from internal phone first

#### Issue: "No audio" or "One-way audio"

**Cause:** RTP/NAT issues

**Solution:**
1. Verify RTP ports 10000-20000 are open
2. Enable `rtp_symmetric=yes` on endpoint
3. Enable `force_rport=yes` on endpoint
4. Check NAT settings in SIP profile

#### Issue: "454 Session Not Authorized"

**Cause:** SIP authentication required

**Solution:**
1. In your app's `.env` file, add:
   ```
   FREEPBX_SIP_USERNAME=twilio
   FREEPBX_SIP_PASSWORD=your_password
   ```
2. Or disable authentication for Twilio endpoint

### 7. Complete PJSIP Configuration Example

For reference, here's a complete working PJSIP config:

```ini
[twilio-endpoint]
type=endpoint
context=from-twilio
disallow=all
allow=ulaw
allow=alaw
allow=opus
transport=transport-udp
direct_media=no
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes

[twilio-aor]
type=aor
contact=sip:twilio@127.0.0.1
max_contacts=10

[twilio-identify]
type=identify
endpoint=twilio-endpoint
match=54.172.60.0/23
match=54.244.51.0/24
match=177.71.206.192/26
match=54.252.254.64/26
match=54.169.127.128/26
```

### 8. Verification Checklist

- [ ] Twilio IP ranges added to FusionPBX ACL
- [ ] UDP port 5060 open in firewall
- [ ] UDP ports 10000-20000 open in firewall
- [ ] Extension 2001 exists and is active
- [ ] SIP profile configured to allow Twilio
- [ ] Dial plan context created for from-twilio
- [ ] Asterisk reloaded after configuration changes
- [ ] Test transfer successful

## Summary

**Minimum Required Configuration:**

1. ✅ Add Twilio IP ranges to FusionPBX ACL/Access Lists
2. ✅ Open UDP 5060 in firewall (server + cloud)
3. ✅ Open UDP 10000-20000 for RTP
4. ✅ Verify extension 2001 exists and is active
5. ✅ Create dial plan context for Twilio calls
6. ✅ Reload Asterisk

**Current Configuration:**
- FusionPBX IP: `136.115.41.45`
- Extension: `2001`
- SIP URI: `sip:2001@136.115.41.45;transport=udp`
- Twilio IP ranges: Whitelisted in FusionPBX

