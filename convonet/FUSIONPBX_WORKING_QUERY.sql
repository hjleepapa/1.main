-- FusionPBX PostgreSQL UPDATE Query (Working Version)

-- First, get the UUID for the external profile
SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external';

-- Then update using the UUID (need to join with v_sip_profiles)
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = '136.113.215.142'
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name IN ('ext-sip-ip', 'ext-rtp-ip');

-- Verify the update
SELECT 
    sp.sip_profile_name,
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name LIKE '%ip%';

-- Alternative: One-liner to do it all at once
-- First, check what needs updating
SELECT 
    sp.sip_profile_name,
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name LIKE '%ip%';

