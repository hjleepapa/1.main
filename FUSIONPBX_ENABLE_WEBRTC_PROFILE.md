# FusionPBX WebRTC Profile Setup - Detailed Steps

## Overview

This guide provides detailed step-by-step instructions to enable and configure the WebRTC (wss) SIP profile in FusionPBX, which allows WebRTC clients to connect directly to FusionPBX.

**Your Configuration:**
- FusionPBX IP: `136.115.41.45`
- WebRTC Port: `7443` (default)
- Domain: `136.115.41.45`

---

## Step-by-Step Instructions

### Step 1: Access FusionPBX Admin Panel

1. **Open your web browser**
2. **Navigate to:** `https://136.115.41.45`
3. **Log in** with your admin credentials
4. **Verify you're in the admin interface**

---

### Step 2: Navigate to SIP Profiles

1. **Click on "Advanced"** in the top menu bar
2. **Click on "SIP Profiles"** from the dropdown menu
3. **You should see a list of SIP profiles** including:
   - `internal` - For internal phones/extensions
   - `external` - For external SIP calls
   - `wss` - WebRTC profile (may not be visible if not enabled)

---

### Step 3: Check Current WebRTC Profile Status

#### Option A: If "wss" profile is already listed:

1. **Look for "wss" in the profile list**
2. **Click on "wss"** to view/edit its settings
3. **Skip to Step 4** to configure settings

#### Option B: If "wss" profile is NOT listed:

The profile exists in FreeSWITCH but may not be enabled in FusionPBX. You need to enable it:

1. **Click on "Default Settings"** (if available) or check System Settings
2. **Look for WebRTC/WSS profile settings**
3. **OR proceed to enable it via database** (see Step 3B below)

#### Option B (Alternative): Enable via FreeSWITCH CLI

```bash
# SSH into your FusionPBX server
ssh root@136.115.41.45

# Access FreeSWITCH CLI
fs_cli

# Check if wss profile exists
sofia status

# If it shows "wss" profile, it's already configured
# If not, you may need to enable it
```

---

### Enable wss Profile via FreeSWITCH CLI - Detailed Steps

If the wss profile doesn't appear in the FusionPBX GUI, or you prefer to enable it via command line, follow these detailed steps:

#### Step 1: SSH into FusionPBX Server

```bash
ssh root@136.115.41.45
```

#### Step 2: Access FreeSWITCH CLI

```bash
# Method 1: Direct fs_cli command
fs_cli

# Method 2: With specific command (non-interactive)
fs_cli -x "sofia status"

# Method 3: One-time command execution
fs_cli -x "command_here"
```

**Note:** If `fs_cli` is not in your PATH, you may need to use the full path:
```bash
/usr/local/freeswitch/bin/fs_cli
# OR
/opt/freeswitch/bin/fs_cli
# OR (if installed via package)
/usr/bin/fs_cli
```

#### Step 3: Check Current Profile Status

```bash
# Check all SIP profiles
sofia status

# Expected output should show profiles like:
# Name         Type      Data        State
# =================================================================
# internal     profile   sip:mod_sofia@127.0.0.1:5060   RUNNING
# external     profile   sip:mod_sofia@127.0.0.1:5080   RUNNING
# wss          profile   sip:mod_sofia@127.0.0.1:7443   STOPPED  ← May show STOPPED or not appear
```

#### Step 4: Check if wss Profile Configuration Exists

```bash
# Check if wss profile configuration file exists
ls -la /etc/freeswitch/sip_profiles/wss.xml

# Or check FusionPBX database
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# Check FreeSWITCH XML directory
ls -la /usr/local/freeswitch/conf/sip_profiles/wss.xml
# OR
ls -la /opt/freeswitch/conf/sip_profiles/wss.xml
```

#### Step 5: Start/Restart wss Profile

If the profile exists but is stopped:

```bash
# Start the wss profile
sofia profile wss start

# OR restart it if it's already running
sofia profile wss restart

# Check status after starting
sofia status profile wss
```

**Expected output after starting:**
```
Profile Name: wss
PROFILE STATE: RUNNING
```

#### Step 6: Create wss Profile if It Doesn't Exist

If the profile doesn't exist, you need to create it. There are two approaches:

##### Option A: Create via FusionPBX Database (Recommended)

```bash
# Connect to FusionPBX database
sudo -u postgres psql fusionpbx

# Insert wss profile into database
INSERT INTO v_sip_profiles (sip_profile_uuid, sip_profile_name, sip_profile_enabled, sip_profile_description)
VALUES (gen_random_uuid(), 'wss', 'true', 'WebRTC WebSocket Secure Profile');

# Exit database
\q

# Reload FreeSWITCH XML from database
fs_cli -x "reloadxml"
fs_cli -x "sofia profile wss start"
```

##### Option B: Create Configuration File Manually

```bash
# Create wss.xml configuration file
cat > /etc/freeswitch/sip_profiles/wss.xml << 'EOF'
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

# Set proper permissions
chown freeswitch:freeswitch /etc/freeswitch/sip_profiles/wss.xml
chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Reload XML configuration
fs_cli -x "reloadxml"

# Start the profile
fs_cli -x "sofia profile wss start"
```

#### Step 7: Verify wss Profile is Running

```bash
# Check profile status
fs_cli -x "sofia status profile wss"

# Expected output:
# Profile Name: wss
# PROFILE STATE: RUNNING
# ...
```

#### Step 8: Check Port is Listening

```bash
# Check if port 7443 is listening
netstat -tlnp | grep 7443

# OR using ss command
ss -tlnp | grep 7443

# Expected output:
# tcp  0  0 0.0.0.0:7443  0.0.0.0:*  LISTEN  12345/freeswitch
# OR
# tcp6  0  0 :::7443  :::*  LISTEN  12345/freeswitch
```

#### Step 9: View Detailed Profile Information

```bash
# Get detailed XML status
fs_cli -x "sofia xmlstatus profile wss"

# This will show comprehensive configuration including:
# - All settings
# - Codecs
# - ACLs
# - TLS configuration
# - RTP settings
```

#### Step 10: Enable wss Profile to Start Automatically

To ensure the profile starts automatically on FreeSWITCH restart:

```bash
# Check if profile is enabled in FusionPBX database
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If enabled is false, update it:
sudo -u postgres psql fusionpbx -c "UPDATE v_sip_profiles SET sip_profile_enabled = 'true' WHERE sip_profile_name = 'wss';"

# Verify
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"
```

#### Step 11: Configure TLS Certificate (If Not Already Done)

The wss profile requires a TLS certificate. Check and configure:

```bash
# Check if certificate exists
ls -la /etc/freeswitch/tls/*.pem
ls -la /etc/freeswitch/tls/wss.*

# If certificate doesn't exist, generate one:
cd /etc/freeswitch/tls
openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"

# Set permissions
chown freeswitch:freeswitch wss.pem
chmod 600 wss.pem

# Restart the profile to load certificate
fs_cli -x "sofia profile wss restart"
```

#### Step 12: Test WebRTC Connection

```bash
# Check for WebSocket connections (after a client connects)
fs_cli -x "sofia status profile wss reg"

# Should show registrations if any clients are connected
```

#### Troubleshooting Commands

If the profile won't start, use these diagnostic commands:

```bash
# Check FreeSWITCH logs for errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -i wss
tail -100 /var/log/freeswitch/freeswitch.log | grep -i 7443

# Check for port conflicts
lsof -i :7443
netstat -tlnp | grep 7443

# Verify FreeSWITCH has permissions
ps aux | grep freeswitch
ls -la /etc/freeswitch/sip_profiles/

# Check configuration syntax
fs_cli -x "reloadxml"
# If errors appear, they will be shown

# Try starting with verbose logging
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"
fs_cli -x "sofia profile wss start"
# Then check logs
tail -f /var/log/freeswitch/freeswitch.log
```

#### Common Issues and Solutions

**Issue 1: Profile shows as STOPPED**
```bash
# Check logs for errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -i error | grep -i wss

# Try restarting
fs_cli -x "sofia profile wss restart"

# Check if port is in use
lsof -i :7443
```

**Issue 2: Port 7443 already in use**
```bash
# Find what's using the port
lsof -i :7443

# Kill the process if it's not FreeSWITCH
kill -9 <PID>

# Or change port in configuration (not recommended)
```

**Issue 3: TLS certificate errors**
```bash
# Check certificate exists and is valid
openssl x509 -in /etc/freeswitch/tls/wss.pem -text -noout

# Regenerate if needed (see Step 11 above)
```

**Issue 4: Permission denied**
```bash
# Check file ownership
ls -la /etc/freeswitch/sip_profiles/wss.xml

# Fix ownership
chown freeswitch:freeswitch /etc/freeswitch/sip_profiles/wss.xml

# Fix certificate permissions
chown freeswitch:freeswitch /etc/freeswitch/tls/wss.pem
chmod 600 /etc/freeswitch/tls/wss.pem
```

#### Quick Reference Commands

```bash
# Start wss profile
fs_cli -x "sofia profile wss start"

# Stop wss profile
fs_cli -x "sofia profile wss stop"

# Restart wss profile
fs_cli -x "sofia profile wss restart"

# Check status
fs_cli -x "sofia status profile wss"

# Check all profiles
fs_cli -x "sofia status"

# Reload XML configuration
fs_cli -x "reloadxml"

# View registrations on wss profile
fs_cli -x "sofia status profile wss reg"

# Get XML status
fs_cli -x "sofia xmlstatus profile wss"
```

---

### Step 4: Configure WebRTC Profile Settings

Once you're on the **wss profile settings page**, configure the following:

#### 4.1 General Settings

**Find the "Settings" table** and configure these parameters:

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **name** | `wss` | ✅ Yes | Profile name |
| **hostname** | `136.115.41.45` | ✅ Yes | Your public IP or domain |
| **domain** | `136.115.41.45` | ✅ Yes | SIP domain |

#### 4.2 Network Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **sip-ip** | `0.0.0.0` | ✅ Yes | Listen on all interfaces |
| **sip-port** | `7443` | ✅ Yes | WSS port (default) |
| **tls** | `true` | ✅ Yes | Enable TLS (required for WSS) |
| **tls-bind-params** | `transport=wss` | ✅ Yes | WSS transport |
| **ext-sip-ip** | `136.115.41.45` | ✅ Yes | External SIP IP |
| **ext-rtp-ip** | `136.115.41.45` | ✅ Yes | External RTP IP |

#### 4.3 WebRTC-Specific Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **enable-100rel** | `true` | ✅ Yes | Enable reliable provisional responses |
| **disable-register** | `false` | ✅ Yes | Allow registrations |
| **rtp-ip** | `0.0.0.0` | ✅ Yes | RTP bind IP |
| **rtp-min-port** | `16384` | ✅ Yes | RTP port range start |
| **rtp-max-port** | `32768` | ✅ Yes | RTP port range end |

#### 4.4 Codec Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **codec-prefs** | `G722,PCMU,PCMA` | ✅ Yes | Preferred codecs |
| **inbound-codec-prefs** | `G722,PCMU,PCMA` | ✅ Yes | Inbound codec preference |
| **outbound-codec-prefs** | `PCMU,PCMA` | ✅ Yes | Outbound codec preference |

**Codec Order:**
- **G722** - High-quality wideband audio (preferred for WebRTC)
- **PCMU** - G.711 μ-law (ULAW) - Standard codec
- **PCMA** - G.711 A-law (ALAW) - Standard codec

#### 4.5 NAT and Firewall Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **local-network-acl** | `localnet.auto` | ✅ Yes | Local network ACL |
| **apply-nat-acl** | `nat.auto` | ✅ Yes | NAT handling |
| **rtp-rewrite-timestamps** | `false` | ✅ Yes | RTP timestamp handling |
| **disable-transcoding** | `false` | ✅ Yes | Allow codec transcoding |

#### 4.6 ACL (Access Control) Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **apply-inbound-acl** | `domains` | ✅ Yes | Allow registered domains |
| **apply-register-acl** | `domains` | ✅ Yes | Allow domain registrations |

**Important:** For WebRTC, you typically want to allow connections from any domain, but you can restrict this if needed.

#### 4.7 Media Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **bypass-media** | `false` | ✅ Yes | Don't bypass media |
| **media-bypass** | `false` | ✅ Yes | Don't bypass media |
| **media-bypass-to** | (empty) | ❌ No | - |
| **media-bypass-from** | (empty) | ❌ No | - |

---

### Step 5: Configure TLS/SSL Certificate

WebRTC requires WSS (WebSocket Secure), which needs a valid TLS certificate.

#### Option A: Use Existing Certificate

If FusionPBX already has an SSL certificate configured:

1. **Check "tls" setting** is set to `true`
2. **Verify certificate path** in system settings
3. **Ensure certificate is valid** for `136.115.41.45`

#### Option B: Generate Self-Signed Certificate (Testing Only)

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# Navigate to FreeSWITCH certs directory
cd /etc/freeswitch/tls

# Generate self-signed certificate (for testing)
openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"

# Set permissions
chown freeswitch:freeswitch wss.pem
chmod 600 wss.pem

# Restart FreeSWITCH
systemctl restart freeswitch
```

#### Option C: Use Let's Encrypt Certificate (Production)

```bash
# Install certbot if not already installed
apt-get install certbot

# Obtain certificate
certbot certonly --standalone -d 136.115.41.45

# Certificate will be in: /etc/letsencrypt/live/136.115.41.45/
# Copy to FreeSWITCH directory
cp /etc/letsencrypt/live/136.115.41.45/fullchain.pem /etc/freeswitch/tls/wss.crt
cp /etc/letsencrypt/live/136.115.41.45/privkey.pem /etc/freeswitch/tls/wss.key

# Set permissions
chown freeswitch:freeswitch /etc/freeswitch/tls/wss.*
chmod 600 /etc/freeswitch/tls/wss.*

# Configure in FusionPBX or wss.xml
```

**In FusionPBX GUI:**
- Find **tls-cert-file** setting
- Set value to: `/etc/freeswitch/tls/wss.crt`
- Find **tls-key-file** setting
- Set value to: `/etc/freeswitch/tls/wss.key`

---

### Step 6: Save and Apply Settings

1. **Click "Save" button** at the bottom of the settings page
2. **Wait for confirmation message**

---

### Step 7: Reload SIP Profile

After saving, you need to reload the SIP profile:

#### Via FusionPBX GUI:

1. **Go to:** **Status → SIP Status**
2. **Find the "wss" profile** in the list
3. **Click "Reload XML"** button for the wss profile
4. **Click "Restart"** button for the wss profile
5. **Verify status shows "RUNNING"**

#### Via FreeSWITCH CLI:

```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# Access FreeSWITCH CLI
fs_cli

# Reload profile
sofia profile wss restart

# Check status
sofia status profile wss
```

**Expected output:**
```
Name    wss
Domain  internal    internal
Auto-NAT    false
DBName  wss
Presence    enabled
Timer-T1    500
Timer-T2    4000
...
```

---

### Step 8: Verify WebRTC Profile is Running

#### Check 1: Via FusionPBX GUI

1. **Go to:** **Status → SIP Status**
2. **Look for "wss" profile**
3. **Status should be:** `RUNNING` (green)
4. **Listen IP:** `0.0.0.0:7443`

#### Check 2: Via FreeSWITCH CLI

```bash
fs_cli -x "sofia status profile wss"
```

**Expected output:**
```
Profile Name: wss
PROFILE STATE: RUNNING
...
```

#### Check 3: Check Port is Listening

```bash
# Check if port 7443 is listening
netstat -tlnp | grep 7443

# Or using ss
ss -tlnp | grep 7443

# Expected output:
# LISTEN  0  ... :::7443  ... freeswitch
```

#### Check 4: Test WebRTC Connection

You can test WebRTC connectivity using:

1. **FusionPBX WebRTC Client:**
   - Navigate to: `https://136.115.41.45/app/calls/`
   - Try to register an extension

2. **Browser Console:**
   - Open browser developer tools
   - Check for WebSocket connections to `wss://136.115.41.45:7443`

---

### Step 9: Firewall Configuration

Ensure port 7443 (WSS) is open in your firewall:

#### UFW (Uncomplicated Firewall):

```bash
sudo ufw allow 7443/tcp
sudo ufw allow 16384:32768/udp  # RTP port range
sudo ufw status
```

#### iptables:

```bash
# Allow WSS port
sudo iptables -A INPUT -p tcp --dport 7443 -j ACCEPT

# Allow RTP port range
sudo iptables -A INPUT -p udp --dport 16384:32768 -j ACCEPT

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

#### Cloud Provider Firewall:

If using a cloud provider (AWS, GCP, Azure):
- **Add inbound rule:** TCP port 7443
- **Add inbound rule:** UDP ports 16384-32768

---

### Step 10: Configure Extensions for WebRTC

To use WebRTC, extensions need to be configured:

1. **Go to:** **Accounts → Extensions**
2. **Click on an extension** (e.g., 2001)
3. **Advanced tab → SIP Profile:**
   - Ensure it can use `wss` profile
   - Or allow both `internal` and `wss`

4. **Settings to check:**
   - **User Context:** `default` (or appropriate context)
   - **Transport:** Allow `wss` transport
   - **Codecs:** Match profile codecs (G722, PCMU, PCMA)

---

## Verification Checklist

After completing all steps, verify:

- [ ] wss profile exists in SIP Profiles list
- [ ] wss profile status is "RUNNING"
- [ ] Port 7443 is listening (check with `netstat` or `ss`)
- [ ] TLS certificate is configured and valid
- [ ] Firewall allows port 7443 (TCP) and 16384-32768 (UDP)
- [ ] External IP `136.115.41.45` is set correctly
- [ ] Codecs G722, PCMU, PCMA are configured
- [ ] ACL settings allow registrations
- [ ] Extension can register via WebRTC

---

## Troubleshooting

### Issue 1: Profile Not Appearing

**Symptom:** wss profile doesn't show in FusionPBX GUI

**Solution:**
```bash
# Check if profile exists in FreeSWITCH
fs_cli -x "sofia status"

# If it exists, it may need to be enabled in database
# Check database:
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_sip_profiles WHERE sip_profile_name = 'wss';"
```

### Issue 2: Profile Won't Start

**Symptom:** wss profile shows "STOPPED" or won't start

**Check logs:**
```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i wss
tail -100 /var/log/freeswitch/freeswitch.log | grep -i 7443
```

**Common issues:**
- Port 7443 already in use
- Invalid TLS certificate
- Missing configuration parameters

### Issue 3: Cannot Connect from Browser

**Symptom:** WebRTC client cannot connect

**Check:**
1. Browser console for WebSocket errors
2. Firewall rules
3. TLS certificate validity
4. CORS settings (if applicable)

**Test connection:**
```bash
# Test WebSocket connection
wscat -c wss://136.115.41.45:7443

# Or using curl
curl -k https://136.115.41.45:7443
```

### Issue 4: No Audio After Connection

**Symptom:** WebRTC connects but no audio

**Check:**
1. RTP port range is open in firewall
2. Codec compatibility between client and server
3. NAT traversal settings
4. Media bypass settings

---

## Complete Configuration Example

Here's a complete example of all settings for the wss profile:

```xml
<!-- This is what the configuration should look like internally -->
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
```

---

## Next Steps

After enabling the WebRTC profile:

1. **Test WebRTC connection** using FusionPBX's built-in client
2. **Configure extensions** to allow WebRTC registration
3. **Implement server-side bridge** (if needed for direct transfer)
4. **Update your application** to use WSS endpoint: `wss://136.115.41.45:7443`

---

## Additional Resources

- **FusionPBX Documentation:** https://docs.fusionpbx.com/
- **FreeSWITCH WebRTC Guide:** https://freeswitch.org/confluence/display/FREESWITCH/WebRTC
- **FusionPBX Forum:** https://www.fusionpbx.com/

---

**Need Help?**

If you encounter issues, check:
1. FreeSWITCH logs: `/var/log/freeswitch/freeswitch.log`
2. FusionPBX logs: `/var/log/fusionpbx/`
3. Browser console for WebSocket errors
4. Firewall rules and port accessibility
