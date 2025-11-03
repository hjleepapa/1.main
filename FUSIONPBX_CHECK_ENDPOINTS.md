# Checking FusionPBX Endpoints and Profile Status

## Understanding the "No Registrations" Message

The `external` SIP profile shows 0 registrations, which is **NORMAL** for Twilio transfers because:

1. ✅ **Twilio doesn't register** - it uses direct SIP INVITE calls
2. ✅ **Your WebRTC extensions register** to the `internal` profile, not `external`
3. ✅ **Twilio calls go to `external`** profile without registration

## What to Check Instead

### 1. Check All SIP Profiles

```bash
fs_cli -x "sofia status"
```

**You should see both profiles:**
- `internal` → For internal phones/extensions (2001)
- `external` → For external SIP calls from Twilio

### 2. Check if Extension 2001 Exists in FusionPBX

```bash
# Via FusionPBX CLI
fs_cli -x "user_exists id 2001 domain-name default"

# Or check PostgreSQL/MariaDB
sudo -u postgres psql fusionpbx
SELECT * FROM v_extensions WHERE extension = '2001';
```

### 3. Check SIP Profile Status

```bash
# See all profiles and their status
fs_cli -x "sofia status"

# See external profile details
fs_cli -x "sofia status profile external"

# See internal profile details (where 2001 would be)
fs_cli -x "sofia status profile internal"
```

### 4. Check if Extension 2001 is Registered to INTERNAL Profile

```bash
# This is where your extension should show up
fs_cli -x "sofia status profile internal reg"

# Should show:
# call-id: xxx@internal
# user: 2001
# contact: sip:2001@...
# registered: true
```

### 5. Check Dial Plan Context

```bash
# See dialplan contexts
fs_cli -x "dialplan_reload"
fs_cli -x "dialplan_loglevel 9"

# Test if extension 2001 is in dialplan
fs_cli -x "dialplan_lookup context=from-external number=2001"
```

## Critical Configuration Check

Since Twilio is calling extension 2001 on the `external` profile, you need:

### Check Dial Plan for Twilio Calls

```bash
# Check what context external calls go to
fs_cli -x "sofia xmlstatus profile external" | grep context

# Should show something like:
# <context>public</context>
# OR
# <context>from-external</context>
```

### Verify Extension 2001 Context

Twilio calls come in on `external` profile → need to route to extension 2001

```bash
# Check the dialplan context for external calls
fs_cli -x "xml_locate directory domain default 2001"
```

## Next Steps

1. **Check extension 2001 exists:**
   ```bash
   sudo -u postgres psql fusionpbx -c "SELECT * FROM v_extensions WHERE extension = '2001';"
   ```

2. **Check which profile extension 2001 uses:**
   - Go to FusionPBX GUI: `Accounts → Extensions → 2001`
   - Check "SIP Profile" setting

3. **Check external profile ACL is configured:**
   ```bash
   fs_cli -x "sofia xmlstatus profile external" | grep apply-inbound-acl
   ```
   Should show: `<apply-inbound-acl>Twilio-SIP</apply-inbound-acl>`

## If Extension 2001 Doesn't Exist

You need to create it in FusionPBX:

1. Login to FusionPBX: `https://136.115.41.45`
2. Go to: `Accounts → Extensions → Add Extension`
3. Create extension:
   - Extension: `2001`
   - Password: (set a secure password)
   - Display Name: "Support Agent"
   - SIP Profile: `internal` (for registration)
   - Context: (usually `default`)
   - Save

4. Create a SIP phone registration or configure a device to use it

## Common Issues

### Issue: Extension Not Reachable from External

**Problem:** Extension 2001 is in `internal` profile, but Twilio calls come to `external` profile

**Solution:** Check dial plan routes external → internal calls

### Issue: "Extension Not Found"

**Check:**
```bash
fs_cli -x "user_exists id 2001 domain-name default"
```

**If false, create the extension in FusionPBX GUI**

### Issue: No Audio After Transfer

**Problem:** RTP ports not open or NAT issues

**Solution:**
- Check firewall allows UDP 10000-20000
- Verify `ext-rtp-ip` is set to public IP in SIP profile

