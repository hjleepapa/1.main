# Fix 403 Forbidden Error: Extension-to-Extension Calling

## 🔴 Problem

**Error:** `403 Forbidden` when trying to call between extensions
- Calling from: `2002@136.115.41.45`
- Calling to: `2001@1361154145` (note: domain format issue)
- Result: `403 Forbidden`

## 🔍 Root Causes of 403 Forbidden

A **403 Forbidden** error means the call is being **blocked/denied**, not a network issue. Common causes:

1. **ACL (Access Control List) blocking** - Extension doesn't have permission to make calls
2. **Wrong domain format** - Notice the called number: `2001@1361154145` (missing dots)
3. **Dialplan context mismatch** - Extension trying to call from wrong context
4. **Extension permissions** - Extension settings blocking outbound calls
5. **SIP profile ACL** - Internal profile ACL blocking calls

## ✅ Diagnostic Steps

### Step 1: Check Domain Format Issue

**Notice the error shows:** `2001@1361154145` (no dots)

**Should be:** `2001@136.115.41.45` (with dots)

This suggests the SIP client is using wrong domain format.

### Step 2: Check Extension 2002 Settings

```bash
# Check if extension 2002 exists and is enabled
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, description FROM v_extensions WHERE extension = '2002';"
```

**Via FusionPBX GUI:**
1. Login: `https://136.115.41.45`
2. Go to: `Accounts → Extensions → 2002`
3. Check:
   - **Enabled:** Should be ✅ Enabled
   - **Caller ID:** Should have valid caller ID
   - **Context:** Should be `default` or appropriate context

### Step 3: Check ACL Settings for Extension 2002

**Via FusionPBX GUI:**
1. Go to: `Accounts → Extensions → 2002`
2. Go to: **Advanced** tab
3. Check:
   - **Caller ID Inbound:** Should allow calls
   - **Caller ID Outbound:** Should allow calls
   - **Reject Caller ID:** Should be empty
   - **Accept Caller ID:** Should allow calls or be empty

### Step 4: Check Internal SIP Profile ACL

The `internal` SIP profile might have ACL blocking:

```bash
# Check internal profile ACL settings
fs_cli -x "sofia xmlstatus profile internal" | grep -i "apply.*acl"
```

**Via FusionPBX GUI:**
1. Go to: `Advanced → SIP Profiles → internal`
2. Check Settings:
   - `apply-inbound-acl` - Should be `domains` or allow extensions
   - `apply-register-acl` - Should be `domains`

### Step 5: Check Dialplan Context

```bash
# Check what context extension 2002 is in
fs_cli -x "user_data 2002@136.115.41.45 var" | grep context

# Check if extension 2001 is accessible from that context
fs_cli -x "xml_locate dialplan default extension 2001"
```

### Step 6: Check Extension Registration

```bash
# Check if extension 2002 is registered
fs_cli -x "sofia status profile internal reg" | grep "2002"

# Should show:
# user: 2002
# contact: sip:2002@...
# registered: true
```

## 🔧 Solutions

### Solution 1: Fix SIP Client Domain Configuration (Most Likely)

The SIP client for extension 2002 is using wrong domain format: `1361154145` instead of `136.115.41.45`

**Fix on the SIP phone/client:**
1. Check SIP account settings
2. Ensure **Domain/Realm** is set to: `136.115.41.45` (with dots)
3. Not: `1361154145` (no dots)
4. Re-register the phone

**Common SIP client settings:**
- **Domain:** `136.115.41.45`
- **Realm:** `136.115.41.45`
- **Proxy:** `136.115.41.45`
- **Username:** `2002`
- **Password:** (your extension password)

### Solution 2: Check Extension 2002 Call Permissions

**Via FusionPBX GUI:**
1. Go to: `Accounts → Extensions → 2002`
2. **Settings** tab:
   - **Outbound CID:** Should be set
   - **Caller ID Name:** Should be set
3. **Advanced** tab:
   - **Reject Caller ID:** (leave empty)
   - **Accept Caller ID:** (leave empty or allow all)
   - **Toll Allow:** Check if there are restrictions

### Solution 3: Check Internal Profile ACL

**Via FusionPBX GUI:**
1. Go to: `Advanced → SIP Profiles → internal`
2. Settings tab:
   - Find: `apply-inbound-acl`
   - Value should be: `domains` (not blocking)
   - Find: `apply-register-acl`
   - Value should be: `domains`

**Or via database:**
```bash
sudo -u postgres psql fusionpbx -c "
SELECT sip_profile_setting_name, sip_profile_setting_value 
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'internal'
AND sip_profile_setting_name LIKE '%acl%';
"
```

### Solution 4: Check Extension Call Forwarding/Blocking

**Via FusionPBX GUI:**
1. Go to: `Accounts → Extensions → 2002`
2. Check:
   - **Do Not Disturb:** Should be **OFF**
   - **Call Forward:** Check if enabled and blocking
   - **Follow Me:** Check if enabled

### Solution 5: Test Extension 2002 Can Make Calls

```bash
# Test if extension 2002 can originate calls
fs_cli -x "originate user/2002@136.115.41.45 &echo()"

# Or test calling extension 2001 from FreeSWITCH CLI
fs_cli -x "originate {origination_caller_id_number=2002,origination_caller_id_name=2002}user/2001@136.115.41.45 &echo()"
```

**If this works:** The issue is with the SIP client configuration
**If this fails:** The issue is with FusionPBX extension settings

### Solution 6: Check Dialplan Permissions

**Via FusionPBX GUI:**
1. Go to: `Dialplan → Destinations`
2. Check if extension 2002 has permission to dial extension 2001

**Or check via database:**
```bash
sudo -u postgres psql fusionpbx -c "
SELECT * FROM v_dialplan_details 
WHERE dialplan_detail_tag = 'action' 
AND dialplan_detail_data LIKE '%2001%';
"
```

### Solution 7: Enable Call Logging

Enable detailed logging to see why 403 is happening:

```bash
# Enable SIP debugging
fs_cli -x "sofia loglevel all 9"

# Enable console logging
fs_cli -x "console loglevel debug"

# Watch logs while attempting call
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden|deny|acl"
```

**Look for:**
- ACL deny messages
- Authentication failures
- Context/permission errors

## 🎯 Most Likely Fix

Based on the error showing `2001@1361154145` (wrong domain format), **the most likely issue is:**

1. **SIP client domain misconfiguration** - Client is using `1361154145` instead of `136.115.41.45`
2. **Fix:** Update SIP client settings to use correct domain format with dots

## 🔍 Quick Verification Checklist

Run through these in order:

- [ ] **Domain format:** SIP client uses `136.115.41.45` (with dots), not `1361154145`
- [ ] **Extension enabled:** Extension 2002 is enabled in FusionPBX
- [ ] **Extension registered:** Extension 2002 shows as registered
- [ ] **Internal profile ACL:** `apply-inbound-acl` is set to `domains` (not blocking)
- [ ] **Extension permissions:** Extension 2002 has outbound call permissions
- [ ] **Do Not Disturb:** DND is OFF for extension 2002
- [ ] **Call blocking:** No call forwarding or blocking enabled
- [ ] **Test from CLI:** Test if FreeSWITCH CLI can make the call successfully

## 📝 Expected Working Configuration

### Extension 2002 SIP Client Settings:
```
Domain/Realm: 136.115.41.45  ← Must have dots!
Username: 2002
Password: (your extension password)
Proxy: 136.115.41.45 (optional)
Transport: UDP (or WSS if using WebRTC)
Port: 5060 (or 7443 for WSS)
```

### FusionPBX Extension 2002 Settings:
```
Extension: 2002
Enabled: ✅ Yes
Context: default
Domain: 136.115.41.45
Do Not Disturb: ❌ No
Call Forward: (disabled or configured correctly)
```

### Internal SIP Profile ACL:
```
apply-inbound-acl: domains
apply-register-acl: domains
```

## 🐛 Still Getting 403?

If you still get 403 after checking everything:

1. **Enable detailed logging** (Solution 7 above)
2. **Attempt the call again**
3. **Check logs for specific deny/block reason**
4. **Look for ACL entries blocking the call**
5. **Check if there's a custom dialplan blocking calls**

Share the log output and I can help identify the specific blocking rule.
