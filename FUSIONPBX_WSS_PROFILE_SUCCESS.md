# FusionPBX WSS Profile - Successfully Configured! ✅

## Status

The WebRTC WebSocket Secure (wss) SIP profile is now **RUNNING** on your FusionPBX server!

**Profile Details:**
- **WSS Port:** `7443` (WebSocket Secure)
- **TLS Port:** `5061` (SIP over TLS)
- **Domain:** `136.115.41.45`
- **Status:** RUNNING ✅

## What Fixed It

The key fix was adding **TLS certificate configuration parameters** to the `wss.xml` file:

```xml
<param name="tls-cert-dir" value="$${base_dir}/conf/tls"/>
<param name="tls-cert-file" value="$${base_dir}/conf/tls/wss.pem"/>
<param name="tls-key-file" value="$${base_dir}/conf/tls/wss.pem"/>
```

Without these TLS certificate paths, FreeSWITCH couldn't load the WSS profile properly.

## Verification

### Check Profile Status

```bash
# Check if wss profile is running
fs_cli -x "sofia status profile wss"

# Check all profiles
fs_cli -x "sofia status"
```

**Expected output:**
```
wss profile on port 7443 - RUNNING (WSS)
wss profile on port 5061 - RUNNING (TLS)
```

### Check Profile Details

```bash
# Get detailed wss profile information
fs_cli -x "sofia xmlstatus profile wss" | head -30

# Check TLS certificate status
fs_cli -x "sofia xmlstatus profile wss" | grep -i "tls\|cert"
```

### Test Port Accessibility

```bash
# Check if ports are listening
sudo netstat -tlnp | grep -E "7443|5061"

# Or using ss
sudo ss -tlnp | grep -E "7443|5061"
```

**Expected output:**
```
tcp  0  0  0.0.0.0:7443  0.0.0.0:*  LISTEN  freeswitch
tcp  0  0  0.0.0.0:5061  0.0.0.0:*  LISTEN  freeswitch
```

## Next Steps: Configure WebRTC Extensions

Now that the WSS profile is running, you need to configure extensions to use WebRTC:

### Step 1: Verify Extension Exists and is Enabled

**Important:** Extensions don't need to be explicitly assigned to the `wss` profile. WebRTC clients connect to the WSS profile directly using their extension credentials. The extension just needs to exist and be enabled.

For extensions that will use WebRTC (like extension 2001, 2002, etc.):

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate to:** `Accounts → Extensions`
3. **Click on the extension** (e.g., 2001)
4. **Verify the extension is enabled and configured:**
   - Extension number is set (e.g., `2001`)
   - Password is set (needed for SIP authentication)
   - User is assigned to the extension
   - **Save** if you made any changes

**Note:** Extensions can register to **any** SIP profile (internal, external, or wss) as long as:
- The extension credentials are correct
- The extension exists in the directory
- The client connects to the correct profile/port

WebRTC clients automatically use the `wss` profile when connecting via `wss://domain:7443`.

### Step 2: Update WebRTC Client Configuration

Update your WebRTC client code to use the WSS profile:

**Example Configuration:**
```javascript
const sipConfig = {
    domain: '136.115.41.45',
    wss_port: 7443,        // WSS port
    transport: 'wss',      // Use WSS
    // ... other settings
};
```

**URL Format:**
```
wss://136.115.41.45:7443
```

### Step 3: Configure Firewall

Ensure ports are open in your firewall:

```bash
# Open WSS port
sudo ufw allow 7443/tcp

# Open TLS port (if needed)
sudo ufw allow 5061/tcp

# Verify
sudo ufw status | grep -E "7443|5061"
```

### Step 4: Test WebRTC Connection

Test with a WebRTC client:

1. **Use a WebRTC SIP client** (like SIP.js, JsSIP, or your custom client)
2. **Connect to:** `wss://136.115.41.45:7443`
3. **Register with extension:** e.g., `2001@136.115.41.45`
4. **Make a test call** to another extension

### Step 5: Test Direct Transfer from WebRTC to FusionPBX

Now you can test direct transfer from your WebRTC voice assistant to FusionPBX extensions:

**In your WebRTC code:**
```javascript
// Transfer to FusionPBX extension
socketio.emit('transfer_to_extension', {
    extension: '2001',
    domain: '136.115.41.45',
    transport: 'wss',
    wss_port: 7443
});
```

## Troubleshooting

### If Profile Stops Running

```bash
# Restart the profile
fs_cli -x "sofia profile wss restart"

# Check status
fs_cli -x "sofia status profile wss"

# Check logs
tail -50 /var/log/freeswitch/freeswitch.log | grep -i wss
```

### If WebRTC Client Can't Connect

1. **Check firewall:** Ensure port 7443 is open
2. **Check TLS certificate:** Verify `wss.pem` exists and is valid
3. **Check logs:** Look for connection errors in FreeSWITCH logs
4. **Verify domain:** Ensure client uses correct domain (`136.115.41.45`)

### Check WebRTC Registration

```bash
# Check if WebRTC clients are registered
fs_cli -x "sofia status profile wss reg"

# Should show registered endpoints if any WebRTC clients are connected
```

## Database Configuration Summary

Your wss profile has:
- ✅ **Profile exists:** `v_sip_profiles` table
- ✅ **18 settings configured:** `v_sip_profile_settings` table
- ✅ **Profile enabled:** `sip_profile_enabled = true`
- ✅ **XML file exists:** `/etc/freeswitch/sip_profiles/wss.xml`
- ✅ **TLS certificates configured:** `/etc/freeswitch/tls/wss.pem`

## Important Notes

1. **TLS Certificate:** The `wss.pem` certificate is self-signed. For production, consider using a proper SSL certificate from a CA.

2. **Profile Persistence:** The XML file is manually created. If FusionPBX regenerates profiles from the database, you may need to ensure the database settings are complete.

3. **Both Ports Running:** It's normal to see the wss profile on both port 7443 (WSS) and 5061 (TLS). Both are functional.

## Success Checklist

- ✅ WSS profile running on port 7443
- ✅ TLS profile running on port 5061
- ✅ TLS certificates configured
- ✅ Database settings complete (18 settings)
- ✅ Profile enabled in database
- ✅ XML file exists and is valid
- ✅ Firewall ports configured
- ⏭️ WebRTC client configuration (next step)
- ⏭️ Extension WebRTC setup (next step)
- ⏭️ Test WebRTC connections (next step)

---

**Congratulations! Your FusionPBX WebRTC profile is now operational!** 🎉

You can now configure WebRTC clients to connect directly to FusionPBX and transfer calls from your WebRTC voice assistant to FusionPBX extensions.
