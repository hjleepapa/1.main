#!/bin/bash
# Fix FusionPBX WSS Profile Binding to 0.0.0.0
# This script forces the WSS profile to bind to 0.0.0.0 instead of the internal IP

echo "=== Fixing WSS Profile Binding ==="

# Get profile UUID
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

if [ -z "$PROFILE_UUID" ]; then
    echo "ERROR: WSS profile not found in database!"
    exit 1
fi

echo "Profile UUID: $PROFILE_UUID"

# Update/add settings to force binding to 0.0.0.0
echo "Updating database settings..."

sudo -u postgres psql fusionpbx << EOF
-- Ensure sip-ip is 0.0.0.0
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '0.0.0.0' 
WHERE sip_profile_uuid = '$PROFILE_UUID' 
AND sip_profile_setting_name = 'sip-ip';

-- Ensure rtp-ip is also 0.0.0.0
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '0.0.0.0' 
WHERE sip_profile_uuid = '$PROFILE_UUID' 
AND sip_profile_setting_name = 'rtp-ip';

-- Add TLS certificate directory (required for proper binding)
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-cert-dir', '\$\${base_dir}/conf/tls', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-cert-dir');

-- Add TLS certificate file
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-cert-file', '\$\${base_dir}/conf/tls/wss.pem', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-cert-file');

-- Add TLS key file
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-key-file', '\$\${base_dir}/conf/tls/wss.pem', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-key-file');
EOF

echo "Database settings updated."

# Manually edit XML to ensure correct binding (FusionPBX may not regenerate correctly)
echo "Updating XML file..."

XML_FILE="/etc/freeswitch/sip_profiles/wss.xml"
BACKUP_FILE="${XML_FILE}.backup.$(date +%Y%m%d_%H%M%S)"

# Backup original
cp "$XML_FILE" "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"

# Find the FreeSWITCH user
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}

# Check if TLS certificate parameters exist in XML
if ! grep -q "tls-cert-dir" "$XML_FILE"; then
    echo "Adding TLS certificate parameters to XML..."
    
    # Add TLS parameters before closing </settings> tag
    sed -i '/<\/settings>/i\
                <param name="tls-cert-dir" value="$${base_dir}/conf/tls"/>\
                <param name="tls-cert-file" value="$${base_dir}/conf/tls/wss.pem"/>\
                <param name="tls-key-file" value="$${base_dir}/conf/tls/wss.pem"/>' "$XML_FILE"
fi

# Ensure sip-ip and rtp-ip are 0.0.0.0 in XML
sed -i 's/<param name="sip-ip" value="[^"]*"\/>/<param name="sip-ip" value="0.0.0.0"\/>/' "$XML_FILE"
sed -i 's/<param name="rtp-ip" value="[^"]*"\/>/<param name="rtp-ip" value="0.0.0.0"\/>/' "$XML_FILE"

# Set permissions
chown $FS_USER:$FS_USER "$XML_FILE"
chmod 644 "$XML_FILE"

echo "XML file updated."

# Reload and restart
echo "Reloading FreeSWITCH XML..."
fs_cli -x "reloadxml" > /dev/null 2>&1
sleep 3

echo "Stopping WSS profile..."
fs_cli -x "sofia profile wss stop" > /dev/null 2>&1
sleep 2

echo "Starting WSS profile..."
fs_cli -x "sofia profile wss start" > /dev/null 2>&1
sleep 2

# Verify binding
echo ""
echo "=== Verification ==="
echo "Checking binding status..."
BIND_STATUS=$(netstat -tlnp 2>/dev/null | grep ":7443" || ss -tlnp 2>/dev/null | grep ":7443")

if echo "$BIND_STATUS" | grep -q "0.0.0.0:7443\|:::7443"; then
    echo "✅ SUCCESS: WSS profile is binding to 0.0.0.0:7443"
    echo ""
    echo "$BIND_STATUS"
elif echo "$BIND_STATUS" | grep -q "7443"; then
    echo "⚠️  WARNING: WSS profile is still binding to a specific IP:"
    echo "$BIND_STATUS"
    echo ""
    echo "This may still work if the IP is accessible externally, but 0.0.0.0 is preferred."
else
    echo "❌ ERROR: WSS profile may not be running or port 7443 is not listening."
fi

echo ""
echo "Profile status:"
fs_cli -x "sofia status profile wss" | grep -E "SIP-IP|RTP-IP|Name"

echo ""
echo "=== Done ==="
