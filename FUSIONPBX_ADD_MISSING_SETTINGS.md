# Add Missing Settings to External SIP Profile

## 🔴 Missing Settings

The following settings don't exist in your FusionPBX external profile yet:
- `bypass-media` = `false`
- `media-bypass` = `false`
- `sip-force-contact` = `136.115.41.45:5060`
- `rtp-force-contact` = `136.115.41.45`
- `accept-blind-reg` = `false`

## ✅ Method 1: Add via FusionPBX GUI (Recommended)

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to SIP Profile:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Click on "Settings" tab** (or find the Settings section)

4. **For each missing setting, click "Add" or "+" button** and add:

### Setting 1: bypass-media
- **Setting Name:** `bypass-media`
- **Value:** `false`
- **Enabled:** ✅ Checked
- **Description:** `Disable media bypass for proper RTP handling`

### Setting 2: media-bypass
- **Setting Name:** `media-bypass`
- **Value:** `false`
- **Enabled:** ✅ Checked
- **Description:** `Disable media bypass for proper RTP handling`

### Setting 3: sip-force-contact
- **Setting Name:** `sip-force-contact`
- **Value:** `136.115.41.45:5060`
- **Enabled:** ✅ Checked
- **Description:** `Force SIP Contact header to use public IP`

### Setting 4: rtp-force-contact
- **Setting Name:** `rtp-force-contact`
- **Value:** `136.115.41.45`
- **Enabled:** ✅ Checked
- **Description:** `Force RTP Contact to use public IP`

### Setting 5: accept-blind-reg
- **Setting Name:** `accept-blind-reg`
- **Value:** `false`
- **Enabled:** ✅ Checked
- **Description:** `Don't accept unauthenticated registrations`

5. **Save all changes:**
   - Click "Save" button at the bottom

6. **Reload FreeSWITCH:**
   - Go to: `Status → SIP Status`
   - Find "external" profile
   - Click "Reload XML"
   - Click "Restart"

## ✅ Method 2: Add via Database (If GUI Doesn't Work)

If the GUI doesn't allow adding new settings, use the database:

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# Connect to PostgreSQL
sudo -u postgres psql fusionpbx
```

### Add bypass-media

```sql
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
    'bypass-media',
    'false',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'bypass-media'
);
```

### Add media-bypass

```sql
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
    'media-bypass',
    'false',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'media-bypass'
);
```

### Add sip-force-contact

```sql
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
    'sip-force-contact',
    '136.115.41.45:5060',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'sip-force-contact'
);
```

### Add rtp-force-contact

```sql
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
    'rtp-force-contact',
    '136.115.41.45',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'rtp-force-contact'
);
```

### Add accept-blind-reg

```sql
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
    'accept-blind-reg',
    'false',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'accept-blind-reg'
);
```

### All-in-One Script

```sql
-- Add all missing settings at once
DO $$
DECLARE
    v_profile_uuid UUID;
BEGIN
    -- Get external profile UUID
    SELECT sip_profile_uuid INTO v_profile_uuid 
    FROM v_sip_profiles 
    WHERE sip_profile_name = 'external';

    -- Add bypass-media
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'bypass-media', 'false', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'bypass-media'
    );

    -- Add media-bypass
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'media-bypass', 'false', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'media-bypass'
    );

    -- Add sip-force-contact
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'sip-force-contact', '136.115.41.45:5060', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'sip-force-contact'
    );

    -- Add rtp-force-contact
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'rtp-force-contact', '136.115.41.45', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'rtp-force-contact'
    );

    -- Add accept-blind-reg
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'accept-blind-reg', 'false', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'accept-blind-reg'
    );

    RAISE NOTICE 'All settings added successfully';
END $$;
```

After running the SQL commands:

```sql
\q
```

```bash
# Reload FreeSWITCH
fs_cli -x "reloadxml"
fs_cli -x "sofia profile external restart"
```

## 🔍 Verify Settings Were Added

```bash
# Check if all settings exist now
fs_cli -x "sofia xmlstatus profile external" | grep -E "bypass-media|media-bypass|sip-force-contact|rtp-force-contact|accept-blind-reg"
```

**Or check via database:**
```sql
SELECT 
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sip_profile_setting_name IN ('bypass-media', 'media-bypass', 'sip-force-contact', 'rtp-force-contact', 'accept-blind-reg')
ORDER BY sip_profile_setting_name;
```

## 📝 What Each Setting Does

### bypass-media = false
- **Purpose:** Disables media bypass, forcing all media to flow through FreeSWITCH
- **Why:** Ensures proper RTP handling and prevents media negotiation issues with Twilio

### media-bypass = false
- **Purpose:** Same as bypass-media (alternative name)
- **Why:** Ensures RTP streams go through FreeSWITCH for proper NAT traversal

### sip-force-contact = 136.115.41.45:5060
- **Purpose:** Forces SIP Contact header to use public IP instead of private IP
- **Why:** Twilio needs to see the public IP in Contact headers to route calls correctly

### rtp-force-contact = 136.115.41.45
- **Purpose:** Forces RTP media to use public IP in SDP (Session Description Protocol)
- **Why:** Ensures Twilio sends RTP packets to your public IP, not private IP

### accept-blind-reg = false
- **Purpose:** Rejects unauthenticated SIP REGISTER requests
- **Why:** Security - prevents unauthorized SIP phones from registering

## 🎯 Summary

Add these 5 settings to your external SIP profile:
1. `bypass-media` = `false`
2. `media-bypass` = `false`
3. `sip-force-contact` = `136.115.41.45:5060`
4. `rtp-force-contact` = `136.115.41.45`
5. `accept-blind-reg` = `false`

Use FusionPBX GUI (Method 1) if possible, or database (Method 2) if GUI doesn't work.
