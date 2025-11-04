# Where to Put external.xml - Important Notes

## ⚠️ IMPORTANT: Don't Manually Edit external.xml if Using FusionPBX

If you're using **FusionPBX**, the `external.xml` file is **automatically generated** from FusionPBX's database. Any manual edits will be **overwritten** when you:
- Click "Reload XML" in FusionPBX GUI
- Restart FreeSWITCH
- FusionPBX regenerates the config

## 📍 File Location (For Reference Only)

If you were to manually edit it (not recommended for FusionPBX), the file location is:

```
/etc/freeswitch/sip_profiles/external.xml
```

**On your FusionPBX server:**
```bash
# The actual file used by FreeSWITCH
/etc/freeswitch/sip_profiles/external.xml

# Your project template file (in your repo)
sambanova/external.xml  # This is just a reference/template
```

## ✅ Correct Way: Configure via FusionPBX GUI

**Instead of copying the XML file, configure via FusionPBX:**

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to SIP Profile:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Edit Settings:**
   - Click on the "external" profile
   - Go to "Settings" tab
   - Find each setting from `external.xml` and update it:
     - `ext-sip-ip` → Set to `136.115.41.45`
     - `ext-rtp-ip` → Set to `136.115.41.45`
     - `sip-ip` → Set to `10.128.0.8` (internal IP)
     - `rtp-ip` → Set to `10.128.0.8` (internal IP)
     - `inbound-codec-prefs` → Set to `PCMU,PCMA`
     - `outbound-codec-prefs` → Set to `PCMU,PCMA`
     - `apply-inbound-acl` → Set to `Twilio-SIP`
     - `bypass-media` → Set to `false`
     - etc.

4. **Save and Reload:**
   - Click "Save" at the bottom
   - Go to: `Status → SIP Status`
   - Find "external" profile
   - Click "Reload XML"
   - Click "Restart"

5. **Verify:**
   ```bash
   fs_cli -x "sofia xmlstatus profile external" | grep -E "ext-sip-ip|ext-rtp-ip"
   ```

## ✅ Alternative: Update Database Directly

If the GUI doesn't work, update the database:

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# Connect to PostgreSQL
sudo -u postgres psql fusionpbx

# Update settings (example for ext-sip-ip)
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = '136.115.41.45',
    sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'ext-sip-ip';

# Repeat for other settings:
# - ext-rtp-ip → 136.115.41.45
# - inbound-codec-prefs → PCMU,PCMA
# - outbound-codec-prefs → PCMU,PCMA
# - apply-inbound-acl → Twilio-SIP
# - bypass-media → false
# - media-bypass → false

\q

# Reload FreeSWITCH
fs_cli -x "reloadxml"
fs_cli -x "sofia profile external restart"
```

## 🔍 Verify Current Settings

To see what FreeSWITCH is actually using (regardless of what's in the XML file):

```bash
fs_cli -x "sofia xmlstatus profile external"
```

This shows the actual active configuration.

## 📝 Why sambanova/external.xml Exists

The `sambanova/external.xml` file in your project is:
- **A template/reference** for what the configuration should look like
- **Documentation** of the required settings
- **Not meant to be copied directly** to the server if using FusionPBX

If you were setting up a **standalone FreeSWITCH** (not FusionPBX), then you would:
1. Copy `sambanova/external.xml` to `/etc/freeswitch/sip_profiles/external.xml`
2. Edit it as needed
3. Reload: `fs_cli -x "reloadxml"`

But since you're using FusionPBX, always configure via the GUI or database.

## 🎯 Summary

- **File location:** `/etc/freeswitch/sip_profiles/external.xml` (on FusionPBX server)
- **Don't edit it manually** - FusionPBX will overwrite it
- **Use FusionPBX GUI** instead: `Advanced → SIP Profiles → external → Settings`
- **Or update database:** `v_sip_profile_settings` table
- **Verify:** `fs_cli -x "sofia xmlstatus profile external"`
