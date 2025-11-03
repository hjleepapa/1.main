# Fix Twilio SIP INVITE to FusionPBX Extensions

## ✅ Good News: Your Extension Works!

Your test call was **successful**:
- Extension 2001 exists and is registered ✅
- Extension can receive calls ✅  
- Dialplan routing works ✅
- RTP/media path works ✅

## 🔴 Problem: Twilio SIP INVITE Not Reaching FusionPBX

Since the internal call works but Twilio transfers fail, the issue is that **Twilio's SIP INVITE requests are either:**
1. Not reaching FusionPBX (firewall/network)
2. Being rejected by FusionPBX (ACL/authentication)
3. Using wrong SIP profile or context

## Diagnostic Steps

### Step 1: Monitor Logs During Twilio Transfer

```bash
# Watch logs in real-time while attempting a Twilio transfer
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "twilio|invite|2001|external"
```

**What to look for:**
- SIP INVITE from Twilio IP addresses (54.172.x.x, 54.244.x.x, etc.)
- "ACL" or "deny" messages
- "NOT_FOUND" or "USER_NOT_REGISTERED" errors
- Any errors related to `external` profile

### Step 2: Check if Twilio INVITE Reaches FusionPBX

```bash
# Enable SIP debugging
fs_cli -x "sofia loglevel all 9"

# Watch for SIP messages from Twilio IPs
tail -f /var/log/freeswitch/freeswitch.log | grep -E "54\.172\.|54\.244\.|177\.71\.|54\.252\.|54\.169\."
```

**If you see INVITE from Twilio IPs:** The issue is ACL or dialplan routing  
**If you DON'T see any INVITE:** The issue is firewall/network (Twilio can't reach FusionPBX)

### Step 3: Verify ACL Configuration

```bash
# Check if ACL is applied to external profile
fs_cli -x "sofia xmlstatus profile external" | grep -i "apply-inbound-acl"

# Should show:
# <apply-inbound-acl>Twilio-SIP</apply-inbound-acl>
```

**If it shows something else or is missing:**
- Go to FusionPBX GUI: `Advanced → SIP Profiles → external → Settings`
- Find `apply-inbound-acl` and set to `Twilio-SIP`
- Reload: `Status → SIP Status → external → Reload XML → Restart`

### Step 4: Test Direct SIP INVITE from External IP

```bash
# This simulates what Twilio does - sends INVITE to external profile
fs_cli -x "originate {origination_caller_id_number=Twilio,origination_caller_id_name=Twilio,context=public,domain_name=136.115.41.45}sofia/external/sip:2001@136.115.41.45 &echo"
```

**Note:** This uses `sofia/external/` instead of `user/` to simulate external SIP call.

## Most Likely Issues & Fixes

### Issue 1: ACL Not Applied to External Profile ❌

**Symptom:** No INVITE messages in logs, or ACL deny messages

**Fix:**
```bash
# Via Database (PostgreSQL)
sudo -u postgres psql fusionpbx

UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'Twilio-SIP',
    sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# If setting doesn't exist, INSERT it
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) VALUES (
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'apply-inbound-acl',
    'Twilio-SIP',
    true
);

\q

# Reload FreeSWITCH
fs_cli -x "reload"
fs_cli -x "sofia profile external restart"

# Verify
fs_cli -x "sofia xmlstatus profile external" | grep apply-inbound-acl
```

### Issue 2: Context Mismatch

**Problem:** External profile uses `public` context, but dialplan doesn't route `public` → extension 2001

**Check dialplan:**
```bash
# Check what dialplan exists for public context
fs_cli -x "xml_locate dialplan public extension 2001"

# Or check via FusionPBX GUI:
# Dialplan → Inbound Routes → Check routes for public context
```

**Fix:** Ensure there's a dialplan route in `public` context that routes to extension 2001:

```xml
<!-- In public context, add extension 2001 -->
<extension name="extension_2001">
  <condition field="destination_number" expression="^2001$">
    <action application="transfer" data="2001 XML default"/>
  </condition>
</extension>
```

### Issue 3: Firewall Blocking Twilio IPs

**Check firewall:**
```bash
# Check if firewall is blocking UDP 5060
sudo iptables -L -n | grep 5060

# Temporarily disable firewall for testing (NOT for production!)
sudo systemctl stop ufw
# OR
sudo iptables -F
```

**Permanent fix:** Configure firewall to allow Twilio IPs:
```bash
# Allow Twilio IP ranges
sudo ufw allow from 54.172.60.0/23 to any port 5060 proto udp
sudo ufw allow from 54.244.51.0/24 to any port 5060 proto udp
sudo ufw allow from 177.71.206.192/26 to any port 5060 proto udp
sudo ufw allow from 54.252.254.64/26 to any port 5060 proto udp
sudo ufw allow from 54.169.127.128/26 to any port 5060 proto udp
```

### Issue 4: External Profile Not Listening on Public IP

**Check:**
```bash
# Check what IP the external profile is bound to
fs_cli -x "sofia status profile external"

# Should show it's listening on 136.115.41.45:5060 (or 0.0.0.0:5060)
```

**If it's only listening on private IP (10.128.x.x):**
```bash
# Check external profile settings
fs_cli -x "sofia xmlstatus profile external" | grep -E "sip-ip|ext-sip-ip"

# Should show:
# <sip-ip>10.128.0.8</sip-ip> (binds to private)
# <ext-sip-ip>136.115.41.45</ext-sip-ip> (advertises public)
```

## Quick Test: Enable Verbose Logging and Try Transfer

```bash
# Terminal 1: Watch logs
tail -f /var/log/freeswitch/freeswitch.log

# Terminal 2: Enable verbose logging
fs_cli -x "console loglevel 9"
fs_cli -x "sofia loglevel all 9"

# Terminal 3: Now attempt a Twilio transfer
# (Make a call to your Twilio number and request transfer)

# Watch Terminal 1 for:
# - SIP INVITE from Twilio IP
# - ACL allow/deny messages
# - Dialplan routing
# - Extension lookup
```

## Expected Log Flow for Successful Transfer

When working correctly, you should see:

```
[INFO] sofia.c: Received SIP INVITE from 54.172.x.x:5060
[DEBUG] sofia.c: ACL check for 54.172.x.x: ALLOW (Twilio-SIP)
[INFO] sofia.c: Routing INVITE to extension 2001
[DEBUG] switch_core_state_machine.c: Dialing user/2001@136.115.41.45
[NOTICE] sofia.c: Channel [sofia/internal/2001@...] has been answered
[INFO] switch_channel.c: Callstate Change RINGING -> ACTIVE
```

## Most Likely Fix Based on Your Setup

Given that:
- ✅ Extension works internally
- ✅ External profile context is `public`
- ❌ Twilio transfers fail

**The most likely issue is:** `apply-inbound-acl` is not set to `Twilio-SIP` on the external profile.

**Run this to fix:**
```bash
sudo -u postgres psql fusionpbx -c "
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'Twilio-SIP',
    sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';
"

fs_cli -x "reload"
fs_cli -x "sofia profile external restart"
```

Then test a Twilio transfer again!
