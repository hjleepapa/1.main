# apply-register-acl Setting for External SIP Profile

## ✅ Recommended Value

**Set `apply-register-acl` to:**
```
domains
```

## 🔍 What Each ACL Setting Does

### `apply-inbound-acl`
- **Controls:** Who can send **SIP INVITE** requests (make calls)
- **Your setting:** `Twilio-SIP` ✅
- **Purpose:** Allows Twilio IP ranges to send calls to your FusionPBX

### `apply-register-acl`
- **Controls:** Who can send **SIP REGISTER** requests (register SIP phones)
- **Recommended:** `domains`
- **Purpose:** Allows SIP phones to register from configured domains

## 📝 Why `domains`?

The `domains` ACL:
1. **References domains configured in FusionPBX** - FusionPBX automatically creates this ACL based on your configured domains
2. **Allows legitimate registrations** - SIP phones from your configured domains can register
3. **Provides security** - Blocks registrations from unknown/unconfigured domains
4. **Standard for external profile** - This is the typical setting for the external SIP profile

## ⚙️ Configuration

### Via FusionPBX GUI

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to SIP Profile:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Find `apply-register-acl` setting:**
   - In the Settings table, find the row: `apply-register-acl`
   - Set **Value** to: `domains`
   - Make sure **Enabled** is checked ✅
   - **Description** can be: "Allow registrations from configured domains"

4. **Save:**
   - Click "Save" at the bottom
   - Go to: `Status → SIP Status`
   - Find "external" profile
   - Click "Reload XML"
   - Click "Restart"

### Via Database

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# Connect to PostgreSQL
sudo -u postgres psql fusionpbx

# Update apply-register-acl setting
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'domains',
    sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-register-acl';

# If setting doesn't exist, INSERT it
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'apply-register-acl',
    'domains',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'apply-register-acl'
);

\q

# Reload FreeSWITCH
fs_cli -x "reloadxml"
fs_cli -x "sofia profile external restart"
```

## 🔍 Verify Setting

```bash
# Check if apply-register-acl is set correctly
fs_cli -x "sofia xmlstatus profile external" | grep -i "apply-register-acl"
```

**Should show:**
```
<apply-register-acl>domains</apply-register-acl>
```

## 📊 Complete ACL Configuration Summary

For your external SIP profile, you should have:

| Setting | Value | Purpose |
|---------|-------|---------|
| `apply-inbound-acl` | `Twilio-SIP` | Allow Twilio IPs to send calls |
| `apply-register-acl` | `domains` | Allow registrations from configured domains |
| `accept-blind-reg` | `false` | Don't accept unauthenticated registrations |

## 🔐 Security Notes

### Why Not Allow All Registrations?

**Don't set `apply-register-acl` to:**
- ❌ Empty/null - Would allow anyone to register (security risk)
- ❌ `any` or `all` - Would allow anyone to register (security risk)
- ❌ `Twilio-SIP` - Twilio doesn't register, so this wouldn't help

**Use `domains` because:**
- ✅ Allows legitimate SIP phones from your configured domains
- ✅ Blocks unknown/unconfigured domains
- ✅ Standard security practice for external SIP profiles

### About `domains` ACL

The `domains` ACL is automatically maintained by FusionPBX based on:
- Domains configured in `Advanced → Domains`
- Each domain you add creates entries in the `domains` ACL
- When a SIP REGISTER request comes in, FusionPBX checks if the domain matches a configured domain

## 🎯 Summary

- **Setting:** `apply-register-acl`
- **Value:** `domains`
- **Location:** FusionPBX GUI → `Advanced → SIP Profiles → external → Settings`
- **Why:** Allows registrations from configured FusionPBX domains while blocking unknown domains
