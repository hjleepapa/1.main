#!/bin/bash
# Force FreeSWITCH WSS Profile to Bind to 0.0.0.0 on Google Cloud VM

echo "=== Fixing WSS Profile Binding to 0.0.0.0 ==="

# Step 1: Update vars.xml to disable interface auto-detection
echo ""
echo "Step 1: Updating FreeSWITCH vars.xml..."
VARS_XML="/etc/freeswitch/vars.xml"
if [ ! -f "$VARS_XML" ]; then
    echo "ERROR: vars.xml not found at $VARS_XML"
    echo "Trying to find it..."
    VARS_XML=$(fs_cli -x "global_getvar conf_dir" | head -1)/vars.xml
    if [ ! -f "$VARS_XML" ]; then
        echo "ERROR: vars.xml not found. Check FreeSWITCH configuration directory."
        exit 1
    fi
fi

# Backup
cp "$VARS_XML" "$VARS_XML.backup.$(date +%Y%m%d_%H%M%S)"
echo "Backup created: $VARS_XML.backup.*"

# Update or add local_ip_v4=0.0.0.0
if grep -q 'local_ip_v4=' "$VARS_XML"; then
    # Update existing
    sed -i 's/<X-PRE-PROCESS cmd="set" data="local_ip_v4=[^"]*"\/>/<X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"\/>/' "$VARS_XML"
    echo "Updated local_ip_v4 in vars.xml"
else
    # Add new (insert before closing tag or at end)
    sed -i '/<\/configuration>/i <X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"/>' "$VARS_XML"
    echo "Added local_ip_v4=0.0.0.0 to vars.xml"
fi

# Step 2: Update wss.xml to add bind-params without maddr
echo ""
echo "Step 2: Updating WSS profile XML..."
WSS_XML="/etc/freeswitch/sip_profiles/wss.xml"
cp "$WSS_XML" "$WSS_XML.backup.$(date +%Y%m%d_%H%M%S)"

# Remove maddr from bind-params if it exists
sed -i 's/<param name="bind-params" value="[^"]*maddr[^"]*"\/>//' "$WSS_XML"

# Add bind-params without maddr (if not exists)
if ! grep -q 'bind-params' "$WSS_XML"; then
    # Add after tls-bind-params
    sed -i '/<param name="tls-bind-params"/a\                <param name="bind-params" value="transport=wss"/>' "$WSS_XML"
    echo "Added bind-params without maddr"
else
    # Update existing to remove maddr
    sed -i 's/<param name="bind-params" value="[^"]*"\/>/<param name="bind-params" value="transport=wss"\/>/' "$WSS_XML"
    echo "Updated bind-params to remove maddr"
fi

# Ensure sip-ip and rtp-ip are 0.0.0.0
sed -i 's/<param name="sip-ip" value="[^"]*"\/>/<param name="sip-ip" value="0.0.0.0"\/>/' "$WSS_XML"
sed -i 's/<param name="rtp-ip" value="[^"]*"\/>/<param name="rtp-ip" value="0.0.0.0"\/>/' "$WSS_XML"

# Set permissions
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
chown $FS_USER:$FS_USER "$WSS_XML"

echo "Updated WSS profile XML"

# Step 3: Restart FreeSWITCH (not just profile reload)
echo ""
echo "Step 3: Restarting FreeSWITCH service..."
systemctl restart freeswitch
sleep 5

# Step 4: Verify
echo ""
echo "=== Verification ==="
echo "Checking binding..."
BIND_STATUS=$(netstat -tlnp 2>/dev/null | grep ":7443" || ss -tlnp 2>/dev/null | grep ":7443")
echo "$BIND_STATUS"

if echo "$BIND_STATUS" | grep -q "0.0.0.0:7443\|:::7443"; then
    echo "✅ SUCCESS: Binding to 0.0.0.0:7443"
else
    echo "⚠️  WARNING: Still binding to specific IP"
    echo ""
    echo "Checking sofia status..."
    fs_cli -x "sofia status profile wss" | grep -E "SIP-IP|BIND-URL"
fi

echo ""
echo "=== Done ==="
