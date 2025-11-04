# FusionPBX WSS Profile Troubleshooting Guide

## Error: "No Such Profile 'wss'"

If you see `[WARNING] sofia.c:6383 No Such Profile 'wss'` even though:
- The profile exists in `v_sip_profiles` table
- The file `/etc/freeswitch/sip_profiles/wss.xml` exists

**The problem:** FreeSWITCH is not loading the profile because:
1. FreeSWITCH reads profiles from a different directory than `/etc/freeswitch/sip_profiles/`
2. The profile settings are missing from the database (`v_sip_profile_settings` table)
3. FreeSWITCH generates profile XML from the database, not from standalone files

**Solution:** Configure the profile via FusionPBX database, not just the file.

### Step 1: Find Where FreeSWITCH Actually Loads Profiles

```bash
# Get FreeSWITCH base directory
fs_cli -x "global_getvar base_dir"

# Check where profiles are actually loaded from
fs_cli -x "global_getvar conf_dir"

# List what profiles FreeSWITCH actually sees
fs_cli -x "sofia status"

# Check internal profile location for reference
ls -la /usr/local/freeswitch/conf/sip_profiles/internal.xml 2>/dev/null
ls -la /opt/freeswitch/conf/sip_profiles/internal.xml 2>/dev/null
ls -la $(fs_cli -x "global_getvar conf_dir" | tail -1)/sip_profiles/ 2>/dev/null
```

### Step 2: Check if Profile Settings Exist in Database

The profile may exist in `v_sip_profiles` but have no settings:

```bash
# Get the profile UUID
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)
echo "Profile UUID: $PROFILE_UUID"

# Check if any settings exist
sudo -u postgres psql fusionpbx -c "SELECT COUNT(*) as setting_count FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID';"

# List all settings (should show multiple rows)
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_setting_name, sip_profile_setting_value FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' ORDER BY sip_profile_setting_name;"
```

### Step 3: Add Missing Profile Settings to Database

If no settings exist, you need to add them. FusionPBX generates the XML from the database:

```bash
# Get profile UUID
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

# Insert all required settings at once
sudo -u postgres psql fusionpbx << EOF
-- Core settings
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
VALUES 
  (gen_random_uuid(), '$PROFILE_UUID', 'name', 'wss', 'true')
  ON CONFLICT DO NOTHING;

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'sip-ip', '0.0.0.0', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'sip-ip');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'sip-port', '7443', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'sip-port');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls', 'true', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-bind-params', 'transport=wss', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-bind-params');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'ext-sip-ip', '136.115.41.45', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'ext-sip-ip');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'ext-rtp-ip', '136.115.41.45', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'ext-rtp-ip');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'domain', '136.115.41.45', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'domain');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'codec-prefs', 'G722,PCMU,PCMA', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'codec-prefs');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'rtp-ip', '0.0.0.0', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'rtp-ip');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'rtp-min-port', '16384', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'rtp-min-port');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'rtp-max-port', '32768', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'rtp-max-port');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'local-network-acl', 'localnet.auto', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'local-network-acl');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'apply-nat-acl', 'nat.auto', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'apply-nat-acl');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'apply-inbound-acl', 'domains', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'apply-inbound-acl');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'apply-register-acl', 'domains', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'apply-register-acl');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'bypass-media', 'false', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'bypass-media');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'media-bypass', 'false', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'media-bypass');
EOF

echo "✅ Profile settings added to database"
```

### Step 4: Regenerate XML from Database

After adding settings, force FusionPBX to regenerate the XML:

```bash
# Reload XML (this should regenerate profiles from database)
fs_cli -x "reloadxml"

# Wait a moment
sleep 2

# Check if profile is now visible
fs_cli -x "sofia status" | grep -i wss

# Try to start
fs_cli -x "sofia profile wss start"
fs_cli -x "sofia status profile wss"
```

### Step 5: Verify Profile Location

Check where the profile XML was actually generated:

```bash
# Find where FreeSWITCH actually loads profiles from
CONF_DIR=$(fs_cli -x "global_getvar conf_dir" | tail -1)
echo "FreeSWITCH conf directory: $CONF_DIR"

# Check if wss.xml was generated there
ls -la "$CONF_DIR/sip_profiles/wss.xml"

# If it exists, check its contents
cat "$CONF_DIR/sip_profiles/wss.xml"
```

---

## Still Failing After Adding Database Settings?

If you've added all settings to the database but still get "Invalid Profile!" or "Failure starting wss", follow these diagnostic steps:

### Diagnostic Step 1: Check Where FreeSWITCH Actually Loads Profiles

```bash
# Get FreeSWITCH base and config directories
fs_cli -x "global_getvar base_dir"
fs_cli -x "global_getvar conf_dir"

# Check common locations
ls -la /etc/freeswitch/sip_profiles/wss.xml 2>/dev/null
ls -la /usr/local/freeswitch/conf/sip_profiles/wss.xml 2>/dev/null
ls -la /opt/freeswitch/conf/sip_profiles/wss.xml 2>/dev/null
ls -la $(fs_cli -x "global_getvar conf_dir" | tail -1)/sip_profiles/wss.xml 2>/dev/null
```

### Diagnostic Step 2: Check if FusionPBX Generated the XML

FusionPBX may need explicit triggering to generate the XML from the database:

```bash
# Check if FusionPBX has a PHP script to regenerate XML
find /var/www/fusionpbx -name "*.php" | xargs grep -l "sip_profiles\|sofia.*xml" | head -5

# Or check if there's a FusionPBX CLI command
fwconsole reload 2>/dev/null || echo "fwconsole not available"

# Check if there's a specific reload command
fs_cli -x "reload mod_sofia"
```

### Diagnostic Step 3: Check the Generated XML File

If the XML file exists, check if it's valid:

```bash
# Find the XML file (try all locations)
XML_FILE=$(find /etc/freeswitch /usr/local/freeswitch/conf /opt/freeswitch/conf 2>/dev/null | grep "sip_profiles/wss.xml" | head -1)

if [ -n "$XML_FILE" ]; then
    echo "Found XML file at: $XML_FILE"
    cat "$XML_FILE"
    
    # Check if it's valid XML
    xmllint --noout "$XML_FILE" 2>&1 || echo "⚠️ XML validation failed"
else
    echo "❌ XML file not found - FusionPBX may not have generated it"
fi
```

### Diagnostic Step 4: Get Detailed Error from Logs

```bash
# Enable maximum logging
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"

# Try to start the profile
fs_cli -x "sofia profile wss start"

# Immediately check logs for detailed error
tail -100 /var/log/freeswitch/freeswitch.log | grep -A 10 -B 10 -iE "wss|error|fail|invalid" | tail -30

# Check specifically for XML parsing errors
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "xml|parse|syntax" | tail -20
```

### Diagnostic Step 4A: Verify FreeSWITCH Sees the Profile During reloadxml

Even if the XML file exists, FreeSWITCH might not be loading it. Check if it's being parsed:

```bash
# Watch the log file in real-time while reloading
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "wss|profile|sip_profiles" &
TAIL_PID=$!

# Reload XML
fs_cli -x "reloadxml"

# Wait a moment
sleep 3

# Kill the tail process
kill $TAIL_PID 2>/dev/null

# Check what profiles FreeSWITCH actually sees
fs_cli -x "sofia status" | head -20
```

### Diagnostic Step 4B: Check sofia.conf.xml Configuration

FusionPBX may use `sofia.conf.xml` to control which profiles are loaded. Check if wss needs to be explicitly included:

```bash
# Find sofia.conf.xml
SOFIA_CONF=$(find /etc/freeswitch -name "sofia.conf.xml" 2>/dev/null | head -1)

if [ -n "$SOFIA_CONF" ]; then
    echo "Found sofia.conf.xml at: $SOFIA_CONF"
    echo "--- Contents ---"
    cat "$SOFIA_CONF"
    
    # Check if profiles are explicitly listed
    echo ""
    echo "--- Profile references ---"
    grep -iE "profile|external|internal|wss" "$SOFIA_CONF"
else
    echo "Could not find sofia.conf.xml in /etc/freeswitch"
    
    # Check autoload_configs directory
    ls -la /etc/freeswitch/autoload_configs/ | grep sofia
fi
```

### Diagnostic Step 4C: Check How FusionPBX Generates Profile XML

FusionPBX might use a PHP script to generate profiles. Check if it's generating them correctly:

```bash
# Find FusionPBX XML generation scripts
find /var/www/fusionpbx -name "*.php" 2>/dev/null | xargs grep -l "sip_profiles\|sofia.*profile" 2>/dev/null | head -5

# Check if there's a specific include mechanism
grep -r "wss\|external\|internal" /etc/freeswitch/autoload_configs/*.xml 2>/dev/null | head -10
```

### Diagnostic Step 4D: Verify XML is Actually Being Read

Check if FreeSWITCH is attempting to read the file:

```bash
# Use strace to see if FreeSWITCH opens the file (if available)
if command -v strace >/dev/null 2>&1; then
    FS_PID=$(pgrep freeswitch | head -1)
    if [ -n "$FS_PID" ]; then
        echo "Watching FreeSWITCH process $FS_PID for file operations..."
        timeout 5 strace -p $FS_PID -e open,openat 2>&1 | grep -i "wss.xml\|sip_profiles" || echo "No file operations detected"
    fi
else
    echo "strace not available"
fi

# Alternative: Check file access times
echo "File access time before reload:"
stat /etc/freeswitch/sip_profiles/wss.xml | grep Access

# Reload
fs_cli -x "reloadxml"

sleep 2

echo "File access time after reload:"
stat /etc/freeswitch/sip_profiles/wss.xml | grep Access
```

---

### Diagnostic Step 5: Check if Profile is Listed in sofia.conf.xml

FreeSWITCH might need the profile to be explicitly listed in `sofia.conf.xml`:

```bash
# Find sofia.conf.xml
SOFIA_CONF=$(find /etc/freeswitch /usr/local/freeswitch/conf /opt/freeswitch/conf 2>/dev/null | grep "autoload_configs/sofia.conf.xml" | head -1)

if [ -n "$SOFIA_CONF" ]; then
    echo "Found sofia.conf.xml at: $SOFIA_CONF"
    cat "$SOFIA_CONF" | grep -A 5 -B 5 "wss\|external\|internal"
else
    echo "Could not find sofia.conf.xml"
fi
```

### Diagnostic Step 6: Manually Generate XML from Database

If FusionPBX isn't generating the XML automatically, you can manually create it:

```bash
# Get all settings from database
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

# Generate XML file from database settings
sudo tee /etc/freeswitch/sip_profiles/wss.xml > /dev/null << 'XML_EOF'
<profile name="wss">
  <settings>
XML_EOF

# Add each setting from database
sudo -u postgres psql fusionpbx -t -c "SELECT '<param name=\"' || sip_profile_setting_name || '\" value=\"' || sip_profile_setting_value || '\"/>' FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_enabled = 'true' ORDER BY sip_profile_setting_name;" | sed 's/^/    /' >> /etc/freeswitch/sip_profiles/wss.xml

# Close the XML
sudo tee -a /etc/freeswitch/sip_profiles/wss.xml > /dev/null << 'XML_EOF'
  </settings>
</profile>
XML_EOF

# Fix permissions
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Verify XML
cat /etc/freeswitch/sip_profiles/wss.xml
xmllint --noout /etc/freeswitch/sip_profiles/wss.xml && echo "✅ XML is valid"

# Reload and try again
fs_cli -x "reloadxml"
sleep 2
fs_cli -x "sofia profile wss start"
fs_cli -x "sofia status profile wss"
```

### Diagnostic Step 7: Check Profile is Enabled in Database

```bash
# Verify profile is enabled
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If not enabled, enable it
sudo -u postgres psql fusionpbx -c "UPDATE v_sip_profiles SET sip_profile_enabled = 'true' WHERE sip_profile_name = 'wss';"
```

### Diagnostic Step 8: Try via FusionPBX GUI

Sometimes the GUI trigger is needed for FusionPBX to recognize the profile:

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate to:** `Advanced → SIP Profiles`
3. **Look for "wss" profile** - if it's there, click on it
4. **If it's NOT there**, the profile may not be fully recognized by FusionPBX
5. **Try clicking "Add" or "+"** to create a new profile named "wss"
6. **Or use the GUI to edit settings** - this might trigger XML regeneration
7. **Go to:** `Status → SIP Status`
8. **Find "wss" profile and click "Reload XML" and "Restart"**

---

# Troubleshooting: wss Profile Fails to Start

## Your Current Issue

- ✅ `wss.xml` file exists at `/etc/freeswitch/sip_profiles/wss.xml`
- ❌ Profile fails to start: "Failure starting wss"
- ❌ `chown freeswitch:freeswitch` fails (user doesn't exist)
- ❌ File not found in standard FreeSWITCH locations

## Diagnostic Steps

### Step 1: Find the Correct FreeSWITCH User

```bash
# Check what user FreeSWITCH runs as
ps aux | grep freeswitch | grep -v grep

# Check systemd service file
systemctl status freeswitch
cat /etc/systemd/system/freeswitch.service | grep User

# OR check init script
cat /etc/init.d/freeswitch | grep USER

# Common FreeSWITCH users:
# - www-data (Debian/Ubuntu with FusionPBX)
# - freeswitch (if installed from source)
# - daemon (some installations)
```

### Step 2: Find the Correct FreeSWITCH Configuration Directory

```bash
# Check where FreeSWITCH is actually installed
which freeswitch
whereis freeswitch

# Check FreeSWITCH CLI for config path
fs_cli -x "global_getvar base_dir"
fs_cli -x "global_getvar conf_dir"

# Check running process for config location
ps aux | grep freeswitch | grep -o '\-conf [^ ]*'

# Common locations:
# - /usr/local/freeswitch/
# - /opt/freeswitch/
# - /var/lib/freeswitch/
# - /etc/freeswitch/ (FusionPBX default)
```

### Step 3: Check FreeSWITCH Logs for Error Details

```bash
# Check recent errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -i wss
tail -100 /var/log/freeswitch/freeswitch.log | grep -i error
tail -100 /var/log/freeswitch/freeswitch.log | grep -i 7443

# Check for TLS certificate errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -i tls
tail -100 /var/log/freeswitch/freeswitch.log | grep -i certificate

# Enable debug logging and try again
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"
fs_cli -x "sofia profile wss start"
tail -50 /var/log/freeswitch/freeswitch.log
```

### Step 4: Check if wss Profile is in FusionPBX Database

```bash
# Complete the database query (if it was interrupted)
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If it doesn't exist, create it:
sudo -u postgres psql fusionpbx << EOF
INSERT INTO v_sip_profiles (sip_profile_uuid, sip_profile_name, sip_profile_enabled, sip_profile_description)
SELECT gen_random_uuid(), 'wss', 'true', 'WebRTC WebSocket Secure Profile'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profiles WHERE sip_profile_name = 'wss');
EOF
```

### Step 5: Verify File Location and Permissions

Since FusionPBX uses `/etc/freeswitch/` as the config directory, that's likely correct. But we need to fix permissions:

```bash
# Find the correct user (most likely www-data for FusionPBX)
FS_USER=$(ps aux | grep freeswitch | grep -v grep | awk '{print $1}' | head -1)
echo "FreeSWITCH runs as user: $FS_USER"

# Fix ownership
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Verify
ls -la /etc/freeswitch/sip_profiles/wss.xml
```

### Step 6: Check TLS Certificate Configuration

The wss profile requires a TLS certificate. Check if it's configured:

```bash
# Check if TLS certificate exists
ls -la /etc/freeswitch/tls/*.pem
ls -la /etc/freeswitch/tls/wss.*

# Check FreeSWITCH TLS directory
find /etc/freeswitch -name "*.pem" -o -name "*.crt" -o -name "*.key" 2>/dev/null

# Check what certificate FreeSWITCH is using
fs_cli -x "sofia xmlstatus profile internal" | grep -i cert
```

### Step 7: Check Port 7443 Availability

```bash
# Check if port 7443 is already in use
sudo lsof -i :7443
sudo netstat -tlnp | grep 7443
sudo ss -tlnp | grep 7443

# If something else is using it, identify and stop it
```

## Solution Steps

### Fix 1: Correct File Permissions (Most Likely Issue)

```bash
# Determine the correct user
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_GROUP=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)

# If that doesn't work, try common ones:
# For FusionPBX on Debian/Ubuntu, it's usually www-data
FS_USER="www-data"
FS_GROUP="www-data"

# Fix ownership
sudo chown $FS_USER:$FS_GROUP /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Verify
ls -la /etc/freeswitch/sip_profiles/wss.xml
```

### Fix 2: Add TLS Certificate Configuration

The wss profile needs TLS certificate settings. Add them to the wss.xml file:

```bash
# Backup the current file
sudo cp /etc/freeswitch/sip_profiles/wss.xml /etc/freeswitch/sip_profiles/wss.xml.backup

# Check if certificate exists
if [ -f /etc/freeswitch/tls/wss.pem ]; then
    CERT_FILE="/etc/freeswitch/tls/wss.pem"
elif [ -f /etc/freeswitch/tls/cert.pem ]; then
    CERT_FILE="/etc/freeswitch/tls/cert.pem"
elif [ -f /etc/freeswitch/tls/tls.pem ]; then
    CERT_FILE="/etc/freeswitch/tls/tls.pem"
else
    echo "Certificate not found. Need to create one."
    CERT_FILE="/etc/freeswitch/tls/wss.pem"
fi

echo "Using certificate: $CERT_FILE"

# Generate certificate if it doesn't exist
if [ ! -f "$CERT_FILE" ]; then
    sudo mkdir -p /etc/freeswitch/tls
    cd /etc/freeswitch/tls
    sudo openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"
    sudo chown $FS_USER:$FS_GROUP wss.pem
    sudo chmod 600 wss.pem
fi

# Update wss.xml to include TLS certificate settings
sudo tee /etc/freeswitch/sip_profiles/wss.xml > /dev/null << 'EOF'
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="tls-cert-dir" value="$${base_dir}/conf/tls"/>
    <param name="tls-cert-file" value="$${base_dir}/conf/tls/wss.pem"/>
    <param name="tls-key-file" value="$${base_dir}/conf/tls/wss.pem"/>
    <param name="tls-ca-file" value="$${base_dir}/conf/tls/cafile.pem"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
EOF

# Fix permissions again
sudo chown $FS_USER:$FS_GROUP /etc/freeswitch/sip_profiles/wss.xml
```

### Fix 3: Ensure Profile Exists in Database

```bash
# Check if profile exists in database
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If it doesn't exist, create it
sudo -u postgres psql fusionpbx << 'SQL'
INSERT INTO v_sip_profiles (sip_profile_uuid, sip_profile_name, sip_profile_enabled, sip_profile_description)
SELECT gen_random_uuid(), 'wss', 'true', 'WebRTC Profile' WHERE NOT EXISTS (SELECT 1 FROM v_sip_profiles WHERE sip_profile_name = 'wss');
SQL

# Verify it was created
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"
```

### Fix 4: Reload and Start Profile

```bash
# Reload XML configuration
fs_cli -x "reloadxml"

# Try starting the profile
fs_cli -x "sofia profile wss start"

# Check status
fs_cli -x "sofia status profile wss"

# Check for errors in logs
tail -50 /var/log/freeswitch/freeswitch.log | grep -i wss
```

## Quick Diagnostic Script

Run this complete diagnostic script:

```bash
#!/bin/bash
echo "=== FreeSWITCH wss Profile Diagnostic ==="
echo ""

echo "1. FreeSWITCH Process Information:"
ps aux | grep '[f]reeswitch' | head -3
echo ""

echo "2. FreeSWITCH User:"
FS_USER=$(ps aux | grep '[f]reeswitch' | grep -v grep | awk '{print $1}' | head -1)
echo "   User: $FS_USER"
echo ""

echo "3. Configuration Directory:"
fs_cli -x "global_getvar base_dir" 2>/dev/null || echo "   Cannot determine (fs_cli may not be accessible)"
fs_cli -x "global_getvar conf_dir" 2>/dev/null || echo "   Cannot determine"
echo ""

echo "4. File Existence:"
ls -la /etc/freeswitch/sip_profiles/wss.xml 2>/dev/null && echo "   ✅ wss.xml exists" || echo "   ❌ wss.xml not found"
echo ""

echo "5. File Permissions:"
ls -la /etc/freeswitch/sip_profiles/wss.xml | awk '{print "   Owner: "$3":"$4" Permissions: "$1}'
echo ""

echo "6. TLS Certificate Check:"
if [ -f /etc/freeswitch/tls/wss.pem ]; then
    echo "   ✅ wss.pem exists"
    ls -la /etc/freeswitch/tls/wss.pem | awk '{print "   Permissions: "$1" Owner: "$3":"$4}'
else
    echo "   ❌ wss.pem not found"
    echo "   Checking for other certificates:"
    ls -la /etc/freeswitch/tls/*.pem 2>/dev/null || echo "   No .pem files found"
fi
echo ""

echo "7. Port 7443 Status:"
if lsof -i :7443 2>/dev/null | grep -q LISTEN; then
    echo "   ⚠️  Port 7443 is already in use:"
    lsof -i :7443
else
    echo "   ✅ Port 7443 is available"
fi
echo ""

echo "8. Profile Status:"
fs_cli -x "sofia status" 2>/dev/null | grep wss || echo "   wss profile not listed"
echo ""

echo "9. Recent Log Errors:"
tail -30 /var/log/freeswitch/freeswitch.log 2>/dev/null | grep -iE "wss|7443|error|failure" | tail -5 || echo "   No recent errors found"
echo ""

echo "10. Database Status:"
sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';" 2>/dev/null || echo "   Cannot check database"
echo ""

echo "=== Diagnostic Complete ==="
```

Save this as `diagnose_wss.sh`, make it executable, and run it:
```bash
chmod +x diagnose_wss.sh
sudo ./diagnose_wss.sh
```

## Most Common Issues and Quick Fixes

### Issue 1: Wrong File Ownership

```bash
# Quick fix - set to www-data (common for FusionPBX)
sudo chown www-data:www-data /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml
```

### Issue 2: Missing TLS Certificate

```bash
# Generate certificate
sudo mkdir -p /etc/freeswitch/tls
cd /etc/freeswitch/tls
FS_USER=$(ps aux | grep '[f]reeswitch' | grep -v grep | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
sudo openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"
sudo chown $FS_USER:$FS_USER wss.pem
sudo chmod 600 wss.pem
```

### Issue 3: Profile Not in Database

```bash
# Add to database
sudo -u postgres psql fusionpbx -c "INSERT INTO v_sip_profiles (sip_profile_uuid, sip_profile_name, sip_profile_enabled, sip_profile_description) SELECT gen_random_uuid(), 'wss', 'true', 'WebRTC Profile' WHERE NOT EXISTS (SELECT 1 FROM v_sip_profiles WHERE sip_profile_name = 'wss');"
fs_cli -x "reloadxml"
```

### Issue 4: Port Conflict

```bash
# Find what's using port 7443
sudo lsof -i :7443
# Kill if needed (replace PID with actual process ID)
# sudo kill -9 <PID>
```

## Expected Resolution Steps

1. **Identify the correct FreeSWITCH user** (likely `www-data`)
2. **Fix file permissions** with the correct user
3. **Generate TLS certificate** if missing
4. **Add TLS certificate settings** to wss.xml
5. **Ensure profile exists in database**
6. **Reload and start the profile**

Run the diagnostic script first to identify the exact issue, then apply the appropriate fix.

---

## Profile Exists in Database But Still Fails to Start

If the wss profile exists in `v_sip_profiles` table but still fails to start, follow these steps:

### Step 1: Check the Actual Error from Logs

```bash
# Enable debug logging and try to start
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"
fs_cli -x "sofia profile wss start"

# Immediately check logs for the error
tail -100 /var/log/freeswitch/freeswitch.log | grep -iE "wss|7443|error|failure|certificate|tls" | tail -20
```

### Step 2: Fix File Permissions

```bash
# Find the correct FreeSWITCH user
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
echo "FreeSWITCH user: $FS_USER"

# If empty or root, use www-data (common for FusionPBX)
if [ -z "$FS_USER" ] || [ "$FS_USER" = "root" ]; then
    FS_USER="www-data"
fi

# Fix ownership
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Verify
ls -la /etc/freeswitch/sip_profiles/wss.xml
```

### Step 3: Check and Generate TLS Certificate

```bash
# Check if TLS certificate exists
ls -la /etc/freeswitch/tls/*.pem 2>/dev/null

# Check what certificates FreeSWITCH uses
fs_cli -x "sofia xmlstatus profile internal" | grep -i cert

# Generate wss.pem if it doesn't exist
if [ ! -f /etc/freeswitch/tls/wss.pem ]; then
    sudo mkdir -p /etc/freeswitch/tls
    cd /etc/freeswitch/tls
    
    FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
    FS_USER=${FS_USER:-www-data}
    
    sudo openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"
    sudo chown $FS_USER:$FS_USER wss.pem
    sudo chmod 600 wss.pem
    
    echo "✅ Certificate created: /etc/freeswitch/tls/wss.pem"
else
    echo "✅ Certificate exists: /etc/freeswitch/tls/wss.pem"
fi
```

### Step 4: Update wss.xml with TLS Certificate Paths

The wss.xml file may need explicit TLS certificate paths. Update it:

```bash
# Backup current file
sudo cp /etc/freeswitch/sip_profiles/wss.xml /etc/freeswitch/sip_profiles/wss.xml.backup

# Find FreeSWITCH base directory
FS_BASE=$(fs_cli -x "global_getvar base_dir" 2>/dev/null)
FS_BASE=${FS_BASE:-/usr/local/freeswitch}

echo "FreeSWITCH base directory: $FS_BASE"

# Update wss.xml with complete configuration including TLS paths
sudo tee /etc/freeswitch/sip_profiles/wss.xml > /dev/null << 'EOF'
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
EOF

# Fix permissions again
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml
```

### Step 5: Reload XML and Start Profile

```bash
# Reload XML configuration
fs_cli -x "reloadxml"

# Wait a moment
sleep 2

# Try to start the profile
fs_cli -x "sofia profile wss start"

# Check status
fs_cli -x "sofia status profile wss"
```

### Step 6: If Still Failing, Check Detailed Error

```bash
# Get detailed error from logs
tail -200 /var/log/freeswitch/freeswitch.log | grep -A 5 -B 5 -iE "wss|7443" | tail -30

# Try with maximum logging
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"
fs_cli -x "reloadxml"
fs_cli -x "sofia profile wss start"
sleep 1
tail -50 /var/log/freeswitch/freeswitch.log | grep -iE "wss|error|fail"
```

### Step 7: Check Port Availability

```bash
# Check if port 7443 is available
sudo lsof -i :7443
sudo netstat -tlnp | grep 7443

# If something is using it, you'll need to stop it first
```

### Step 8: Alternative - Check if Profile is Enabled in Settings

Sometimes FusionPBX needs the profile settings to be configured even if the profile exists:

```bash
# Check if there are any settings for the wss profile
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_setting_name, sip_profile_setting_value FROM v_sip_profile_settings WHERE sip_profile_uuid = (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss');"
```

If no settings exist, you may need to add them via FusionPBX GUI or add them manually to the database.

---

## Complete Fix Script (Run All at Once)

If you want to run everything at once, use this script:

```bash
#!/bin/bash
echo "=== Fixing wss Profile ==="

# Step 1: Find FreeSWITCH user
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
echo "Using user: $FS_USER"

# Step 2: Fix file permissions
echo "Fixing file permissions..."
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Step 3: Ensure TLS certificate exists
echo "Checking TLS certificate..."
if [ ! -f /etc/freeswitch/tls/wss.pem ]; then
    sudo mkdir -p /etc/freeswitch/tls
    cd /etc/freeswitch/tls
    sudo openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"
    sudo chown $FS_USER:$FS_USER wss.pem
    sudo chmod 600 wss.pem
    echo "✅ Certificate created"
else
    echo "✅ Certificate exists"
fi

# Step 4: Reload and start
echo "Reloading XML..."
fs_cli -x "reloadxml"
sleep 2

echo "Starting wss profile..."
fs_cli -x "sofia profile wss start"
sleep 2

# Step 5: Check status
echo ""
echo "=== Status Check ==="
fs_cli -x "sofia status profile wss"

# Step 6: Check for errors
echo ""
echo "=== Recent Errors ==="
tail -30 /var/log/freeswitch/freeswitch.log | grep -iE "wss|7443|error" | tail -5

echo ""
echo "=== Fix Complete ==="
```

Save as `fix_wss.sh`, make executable, and run:
```bash
chmod +x fix_wss.sh
sudo ./fix_wss.sh
```

---

### Most Likely Fix: Ensure Database Settings Trigger XML Generation

Since FusionPBX generates profiles from the database, ensure all required settings exist and trigger regeneration:

```bash
# Verify all settings are in database
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_setting_name, sip_profile_setting_value FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_enabled = 'true' ORDER BY sip_profile_setting_name;"

# Check if profile is enabled
sudo -u postgres psql fusionpbX -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If profile is disabled, enable it
sudo -u postgres psql fusionpbx -c "UPDATE v_sip_profiles SET sip_profile_enabled = 'true' WHERE sip_profile_name = 'wss';"

# Then trigger regeneration via GUI or find the PHP script
```

### 🔧 DIRECT FIX: XML File Exists But Not Loading

If `wss.xml` exists in `/etc/freeswitch/sip_profiles/` but FreeSWITCH still can't see it, the XML might be failing to parse silently. Common issues:

#### Issue 1: Missing TLS Certificate Configuration

WSS profiles require TLS certificates. Add TLS certificate paths to your XML:

```bash
# Check if TLS certificates exist
ls -la /etc/freeswitch/tls/*.pem

# Get FreeSWITCH base directory for certificate paths
BASE_DIR=$(fs_cli -x "global_getvar base_dir" | tail -1)
echo "Base dir: $BASE_DIR"

# Update wss.xml with TLS certificate configuration
sudo tee /etc/freeswitch/sip_profiles/wss.xml > /dev/null << EOF
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="tls-cert-dir" value="\$\${base_dir}/conf/tls"/>
    <param name="tls-cert-file" value="\$\${base_dir}/conf/tls/wss.pem"/>
    <param name="tls-key-file" value="\$\${base_dir}/conf/tls/wss.pem"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
EOF

# Fix permissions
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Reload and try
fs_cli -x "reloadxml"
sleep 2
fs_cli -x "sofia profile wss start"
fs_cli -x "sofia status profile wss"
```

#### Issue 2: Check for XML Parsing Errors

Enable XML debug logging to see if there are parsing errors:

```bash
# Enable XML debug
fs_cli -x "console loglevel debug"
fs_cli -x "loglevel 7"

# Reload XML and watch for errors
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "wss|xml|parse|error|syntax" &
TAIL_PID=$!

fs_cli -x "reloadxml"
sleep 3
kill $TAIL_PID

# Check for specific XML parsing errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -A 5 -B 5 -iE "wss|xml.*error|parse.*error" | tail -20
```

#### Issue 3: Verify XML is Being Included

Check if the XML file is actually being read during reloadxml:

```bash
# Check file permissions
ls -la /etc/freeswitch/sip_profiles/wss.xml

# Verify the include pattern matches
echo "Checking if wss.xml matches include pattern..."
ls -1 /etc/freeswitch/sip_profiles/*.xml | grep -v "\.noload"

# Check if wss.xml is listed
ls -1 /etc/freeswitch/sip_profiles/*.xml | grep wss

# Test XML syntax manually (if xmllint is available)
which xmllint && xmllint --noout /etc/freeswitch/sip_profiles/wss.xml || echo "xmllint not available - checking manually..."

# Check for common XML issues
grep -n "<param\|</param\|<profile\|</profile\|<settings\|</settings" /etc/freeswitch/sip_profiles/wss.xml
```

#### Issue 4: Profile Not Appearing in sofia status After reloadxml

If `wss` doesn't appear in `sofia status` after `reloadxml`, the XML file isn't being parsed. This could mean:

1. **FusionPBX is overwriting the file** - FusionPBX regenerates profiles from the database and may overwrite manual XML files
2. **XML syntax error** - A syntax error prevents the file from being parsed, but no error is shown
3. **Include pattern issue** - The file doesn't match the include pattern

**Fix: Check if FusionPBX is regenerating the file:**

```bash
# Monitor if the file gets overwritten during reloadxml
md5sum /etc/freeswitch/sip_profiles/wss.xml
BEFORE_MD5=$(md5sum /etc/freeswitch/sip_profiles/wss.xml | awk '{print $1}')

fs_cli -x "reloadxml"
sleep 2

AFTER_MD5=$(md5sum /etc/freeswitch/sip_profiles/wss.xml | awk '{print $1}')

if [ "$BEFORE_MD5" != "$AFTER_MD5" ]; then
    echo "⚠️ WARNING: File was modified during reloadxml!"
    echo "FusionPBX is overwriting your manual XML file"
    echo "You need to configure via FusionPBX GUI or database instead"
else
    echo "✅ File was not modified"
fi
```

**Fix: Check if there's an XML parsing error that's silent:**

```bash
# Enable maximum XML logging
fs_cli -x "console loglevel debug"
fs_cli -x "loglevel 7"

# Watch for XML parsing errors
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "wss|xml|parse|error|sip_profiles" &
TAIL_PID=$!

fs_cli -x "reloadxml"
sleep 3
kill $TAIL_PID

# Check specifically for wss-related errors
tail -200 /var/log/freeswitch/freeswitch.log | grep -A 10 -B 10 -iE "wss|sip_profiles.*wss" | tail -30
```

**Fix: Try using FusionPBX GUI to create the profile**

Since FusionPBX generates profiles dynamically, the most reliable way is through the GUI:

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate to:** `Advanced → SIP Profiles`
3. **Click "Add" or "+"** to create a new profile
4. **Set Profile Name:** `wss`
5. **Configure all settings via GUI**
6. **Save**
7. **Go to:** `Status → SIP Status`
8. **Click "Reload XML"** at the top
9. **Find "wss" profile and click "Restart"**

**Fix: Check if profile needs to be in a specific database state**

FusionPBX might require specific database entries beyond just the profile and settings:

```bash
# Check what tables are involved
sudo -u postgres psql fusionpbx -c "\dt" | grep -i "sip\|profile"

# Check if there are any constraints or triggers
sudo -u postgres psql fusionpbx -c "SELECT tablename, indexname FROM pg_indexes WHERE tablename LIKE '%sip%profile%';"

# Check if internal/external profiles have something wss doesn't
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_sip_profiles WHERE sip_profile_name IN ('internal', 'external', 'wss') ORDER BY sip_profile_name;"

# Compare settings count
sudo -u postgres psql fusionpbx -c "
SELECT 
    sp.sip_profile_name,
    COUNT(sps.sip_profile_setting_uuid) as setting_count
FROM v_sip_profiles sp
LEFT JOIN v_sip_profile_settings sps ON sp.sip_profile_uuid = sps.sip_profile_uuid
WHERE sp.sip_profile_name IN ('internal', 'external', 'wss')
GROUP BY sp.sip_profile_name
ORDER BY sp.sip_profile_name;"
```

---
