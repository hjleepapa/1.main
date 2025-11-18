#!/bin/bash
# Quick Fix: Bind WSS Profile to Public IP (since alias is on interface)

echo "=== Binding WSS Profile to Public IP ==="

PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

if [ -z "$PROFILE_UUID" ]; then
    echo "ERROR: WSS profile not found!"
    exit 1
fi

echo "Updating sip-ip to 136.115.41.45..."

sudo -u postgres psql fusionpbx << EOF
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '136.115.41.45' 
WHERE sip_profile_uuid = '$PROFILE_UUID' 
AND sip_profile_setting_name = 'sip-ip';

UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '136.115.41.45' 
WHERE sip_profile_uuid = '$PROFILE_UUID' 
AND sip_profile_setting_name = 'rtp-ip';
EOF

echo "Reloading profile..."
fs_cli -x "reloadxml"
sleep 3
fs_cli -x "sofia profile wss stop"
sleep 2
fs_cli -x "sofia profile wss start"
sleep 3

echo ""
echo "=== Verification ==="
netstat -tlnp | grep 7443
fs_cli -x "sofia status profile wss" | grep -E "SIP-IP|BIND-URL"
