# FusionPBX Configuration for Twilio Call Transfer

## Overview

This guide configures FusionPBX at **136.115.41.45** to accept SIP transfers from Twilio voice calls.

**Flow:**
```
Twilio Voice Call → AI Agent → Transfer to FusionPBX Extension 2001
```

## Required Configuration Steps

### Step 1: Create Access Control List (ACL) ✅ DONE

You've already created the `Twilio-SIP` access list in FusionPBX:

**Access Control Configuration:**
- **Name**: `Twilio-SIP`
- **Default**: `allow`
- **IP Ranges (CIDR)**:
  ```
  54.172.60.0/23
  54.244.51.0/24
  177.71.206.192/26
  54.252.254.64/26
  54.169.127.128/26
  ```
- **Description**: `Twilio-SIP`

This is **correctly configured**. ✅

---

### Step 2: Configure SIP Profile to Apply the ACL

**This is the critical missing step!** You need to apply the `Twilio-SIP` ACL to your SIP profile.

#### Option A: Via FusionPBX Web GUI (Recommended)

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to SIP Profiles:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Find the `external` SIP Profile Settings**

4. **Locate "Settings" Section:**
   Look for a setting called `apply-inbound-acl` in the Settings table.

5. **Update the Setting:**
   - Find the row: `apply-inbound-acl`
   - Change its **Value** from whatever it currently is to: `Twilio-SIP`
   - Make sure **Enabled** is set to `True`
   - Keep **Description** empty or add "Allow Twilio SIP traffic"

6. **Also Check These Settings:**
   - `apply-nat-acl`: Should be `nat.auto` or empty (Enabled: True)
   - `local-network-acl`: Should be `localnet.auto` (Enabled: True)
   - `ext-sip-ip`: Should be your public IP `136.115.41.45` (Enabled: True)
   - `ext-rtp-ip`: Should be your public IP `136.115.41.45` (Enabled: True)

7. **Save and Apply:**
   - Click "Save" button at the bottom
   - Go to: `Status → SIP Status`
   - Find the "external" profile
   - Click "Reload XML" button
   - Click "Restart" button

#### Option B: Via Database (If GUI Doesn't Work)

If the FusionPBX GUI doesn't allow you to modify the setting, update it via database:

**For PostgreSQL:**
```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# Connect to PostgreSQL
sudo -u postgres psql fusionpbx

# Check current apply-inbound-acl setting
SELECT 
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value,
    sps.sip_profile_setting_enabled
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Update to use Twilio-SIP ACL
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'Twilio-SIP'
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Make sure it's enabled
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Verify the change
SELECT 
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value,
    sps.sip_profile_setting_enabled
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Exit PostgreSQL
\q

# Reload FreeSWITCH
fs_cli -x "reload"
fs_cli -x "reload mod_sofia"
```

**For MySQL/MariaDB:**
```bash
# Connect to MySQL
mysql -u root -p fusionpbx

# Update apply-inbound-acl setting
UPDATE v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
SET sps.sip_profile_setting_value = 'Twilio-SIP',
    sps.sip_profile_setting_enabled = true
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Verify
SELECT 
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value,
    sps.sip_profile_setting_enabled
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Exit MySQL
EXIT;
```

---

### Step 3: Open Firewall Ports

#### On the Server/VPS Level

**Open UDP Port 5060 for SIP:**
```bash
# Using ufw
sudo ufw allow 5060/udp

# Using iptables
sudo iptables -A INPUT -p udp --dport 5060 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 10000:20000 -j ACCEPT

# Save iptables rules (on Debian/Ubuntu)
sudo iptables-save > /etc/iptables/rules.v4
```

**Open RTP Ports 10000-20000:**
```bash
sudo ufw allow 10000:20000/udp
```

#### If Using Cloud Provider (Google Cloud, AWS, Azure, etc.)

Create firewall rules to allow SIP traffic:

**Google Cloud:**
```bash
gcloud compute firewall-rules create allow-twilio-sip \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=udp:5060 \
    --source-ranges=54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26 \
    --target-tags=freepbx

gcloud compute firewall-rules create allow-twilio-rtp \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=udp:10000-20000 \
    --source-ranges=54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26 \
    --target-tags=freepbx
```

**AWS:**
```bash
# Create Security Group rules for SIP
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxx \
    --protocol udp \
    --port 5060 \
    --source-group sg-twilio \
    --cidr 54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26
```

---

### Step 4: Verify Extension 2001 Exists

**Via FusionPBX Web GUI:**
1. Login to `https://136.115.41.45`
2. Go to: `Accounts → Extensions`
3. Search for extension `2001`
4. Verify:
   - Extension is **active**
   - Has a valid **device/endpoint** assigned
   - Is assigned to a valid **dial plan context**

**Or check via SSH:**
```bash
ssh root@136.115.41.45

# Check FreeSWITCH endpoints
fs_cli -x "sofia status profile external reg"

# Or check via Asterisk (if using)
asterisk -rx "pjsip list endpoints" | grep 2001
```

---

### Step 5: Test Configuration

#### Test 1: Verify SIP Port is Open

From your local machine:
```bash
nc -zuv 136.115.41.45 5060
```

**Expected:** `Connection to 136.115.41.45 5060 port [udp/sip] succeeded!`

#### Test 2: Check FreeSWITCH SIP Profile

```bash
ssh root@136.115.41.45
fs_cli -x "sofia xmlstatus profile external"
```

Look for:
- `<ext-sip-ip>136.115.41.45</ext-sip-ip>` ✅
- `<apply-inbound-acl>Twilio-SIP</apply-inbound-acl>` ✅

#### Test 3: Monitor FreeSWITCH Logs in Real-Time

```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# Watch FreeSWITCH logs
tail -f /var/log/freeswitch/freeswitch.log | grep -i twilio

# Or use FreeSWITCH CLI
fs_cli -x "console loglevel 7"
```

#### Test 4: Make Test Transfer from Twilio

1. Make a test call to your Twilio number
2. Say "transfer me to agent" or similar
3. Watch the logs in real-time:

```bash
# On FusionPBX server
fs_cli -x "console loglevel 9"
```

**Look for:**
- SIP INVITE from Twilio IP (54.172.x.x or 54.244.x.x)
- ACK from FusionPBX
- Extension 2001 receiving the call
- Call being bridged successfully

---

### Step 6: Monitor Transfer Logs

**Watch FreeSWITCH CLI during transfer:**
```bash
ssh root@136.115.41.45
fs_cli
```

In the FreeSWITCH CLI, you should see:
```
[SIP]
[INVITE] from 54.172.x.x:5060
[200 OK] sending to 54.172.x.x:5060
[ACK] received
Extension 2001 is ringing
Call answered
RTP media established
```

---

### Troubleshooting

#### Issue: "Transfer failed" - SIP INVITE Rejected

**Symptoms:** Logs show `status=failed` in transfer callback

**Causes & Solutions:**

1. **Twilio IP not whitelisted**
   - Verify `Twilio-SIP` ACL exists in `Advanced → Firewall → Access Lists`
   - Verify `apply-inbound-acl` setting in SIP profile = `Twilio-SIP`

2. **Firewall blocking SIP**
   - Check UDP 5060 is open: `nc -zuv 136.115.41.45 5060`
   - Check cloud provider firewall rules
   - Check fail2ban isn't blocking: `sudo fail2ban-client status sshd`

3. **Extension 2001 doesn't exist**
   - Verify extension exists in `Accounts → Extensions`
   - Check extension is active and has valid device
   - Test extension from internal phone first

4. **FreeSWITCH not reloaded**
   - Go to `Status → SIP Status`
   - Click "Reload XML"
   - Click "Restart" for external profile

#### Issue: "403 Forbidden" or "401 Unauthorized"

**Cause:** SIP authentication required

**Solution:**
1. Set SIP authentication in your app's `.env`:
   ```
   FREEPBX_SIP_USERNAME=twilio
   FREEPBX_SIP_PASSWORD=your_secure_password
   ```
2. Create a SIP user in FusionPBX for Twilio
3. Or configure the extension to allow anonymous calls

#### Issue: "No audio" or "One-way audio"

**Cause:** RTP/NAT issues

**Solution:**
1. Verify RTP ports 10000-20000 are open in firewall
2. Check `ext-sip-ip` and `ext-rtp-ip` settings in SIP profile
3. Enable `rtp-symmetric` in SIP profile
4. Check NAT settings in cloud provider

#### Issue: "Extension not found" or "408 Request Timeout"

**Cause:** Extension 2001 doesn't exist, isn't registered, or wrong context

**Solution:**
1. Verify extension exists: `Accounts → Extensions → 2001`
2. Check extension device is online: `Status → Registrations`
3. Verify dial plan context is correct
4. Test from internal phone first

---

### Summary Checklist

- [x] ✅ **Step 1**: Access Control List `Twilio-SIP` created with 5 Twilio IP ranges
- [ ] ⚠️ **Step 2**: SIP Profile `external` → `apply-inbound-acl` set to `Twilio-SIP` ← **CRITICAL MISSING STEP**
- [ ] **Step 3**: UDP port 5060 open in server firewall
- [ ] **Step 4**: UDP ports 10000-20000 open for RTP
- [ ] **Step 5**: UDP ports open in cloud provider firewall (if applicable)
- [ ] **Step 6**: Extension 2001 exists and is active
- [ ] **Step 7**: FreeSWITCH reloaded after configuration changes
- [ ] **Step 8**: Test transfer successful

**Current Status:**
- FusionPBX IP: `136.115.41.45`
- Extension: `2001`
- SIP URI: `sip:2001@136.115.41.45;transport=udp`
- Access List: `Twilio-SIP` ✅ Created
- Missing: SIP Profile ACL configuration ⚠️

**Next Step:** Configure the `apply-inbound-acl` setting in your SIP profile (Step 2).
