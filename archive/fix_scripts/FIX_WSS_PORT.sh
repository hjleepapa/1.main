#!/bin/bash
# Fix WSS profile TLS-BIND-URL to use port 7443 instead of 5061

PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

echo "=== Fixing WSS Profile Port ==="
echo "Profile UUID: $PROFILE_UUID"

# Add TLS certificate settings to database
sudo -u postgres psql fusionpbx << EOF
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-cert-dir', '\$\${base_dir}/conf/tls', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-cert-dir');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-cert-file', '\$\${base_dir}/conf/tls/wss.pem', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-cert-file');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-key-file', '\$\${base_dir}/conf/tls/wss.pem', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-key-file');
EOF

# Add to XML as well
WSS_XML="/etc/freeswitch/sip_profiles/wss.xml"
if ! grep -q "tls-cert-dir" "$WSS_XML"; then
    cp "$WSS_XML" "$WSS_XML.backup.$(date +%Y%m%d_%H%M%S)"
    sed -i '/<\/settings>/i\
                <param name="tls-cert-dir" value="$${base_dir}/conf/tls"/>\
                <param name="tls-cert-file" value="$${base_dir}/conf/tls/wss.pem"/>\
                <param name="tls-key-file" value="$${base_dir}/conf/tls/wss.pem"/>' "$WSS_XML"
    FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
    FS_USER=${FS_USER:-www-data}
    chown $FS_USER:$FS_USER "$WSS_XML"
fi

# Restart profile
echo "Restarting WSS profile..."
fs_cli -x "reloadxml"
fs_cli -x "sofia profile wss stop"
sleep 2
fs_cli -x "sofia profile wss start"
sleep 3

# Verify
echo ""
echo "=== Verification ==="
echo "TLS-BIND-URL:"
fs_cli -x "sofia status profile wss" | grep "TLS-BIND-URL"
echo ""
echo "Listening ports:"
ss -tlnp | grep -E "7443|5061"
