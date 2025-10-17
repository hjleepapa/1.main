# FreePBX WebRTC Login Failure - Troubleshooting Guide

## Issue
WebRTC phone cannot login to FreePBX at IP: **198.27.161.100** or **34.26.59.14**

## Understanding the Problem

WebRTC phones require:
1. **WebSocket Secure (WSS)** connection on port **7443/TCP** (or 8089)
2. **Valid SSL certificate**
3. **WebRTC enabled** in FreePBX
4. **Firewall rules** allowing WSS traffic
5. **STUN/TURN servers** for NAT traversal

---

## Step 1: Check Which IP to Use

### Question: Is 198.27.161.100 your FreePBX server?

```bash
# Check if this IP responds
ping 198.27.161.100
ping 34.26.59.14

# The IP that responds is your FreePBX server
```

**For this guide, I'll assume your FreePBX is at: 34.26.59.14**
(If it's 198.27.161.100, replace all instances below)

---

## Step 2: Google Cloud Firewall - Open WebRTC Ports

### 2.1 Create Firewall Rule for WSS (Port 7443/TCP)

**Via Google Cloud Console:**
```
VPC Network → Firewall → Create Firewall Rule

Name: allow-webrtc-wss
Description: Allow WebRTC WebSocket Secure traffic
Direction: Ingress
Action: Allow
Targets: All instances (or tag: freepbx)
Source IP ranges: 0.0.0.0/0 (allow from anywhere)
Protocols and ports: TCP: 7443

Click: Create
```

### 2.2 Create Firewall Rule for HTTP Management (Port 8089)

```
Name: allow-freepbx-https
Direction: Ingress
Action: Allow
Protocols and ports: TCP: 8089

Click: Create
```

### 2.3 Via gcloud CLI (Alternative)

```bash
# Allow WSS port 7443
gcloud compute firewall-rules create allow-webrtc-wss \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=tcp:7443 \
    --source-ranges=0.0.0.0/0

# Allow HTTPS management port 8089
gcloud compute firewall-rules create allow-freepbx-https \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=tcp:8089 \
    --source-ranges=0.0.0.0/0
```

---

## Step 3: Configure FreePBX for WebRTC

### 3.1 Enable WebSocket Support in Asterisk

SSH into your FreePBX VM:
```bash
gcloud compute ssh your-freepbx-instance
```

Edit `/etc/asterisk/http.conf`:
```bash
sudo nano /etc/asterisk/http.conf
```

Add or update:
```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
tlsenable=yes
tlsbindaddr=0.0.0.0:8089
tlscertfile=/etc/asterisk/keys/asterisk.pem
tlsprivatekey=/etc/asterisk/keys/asterisk.key
```

### 3.2 Configure WebSocket Transport in PJSIP

Edit `/etc/asterisk/pjsip.conf`:
```bash
sudo nano /etc/asterisk/pjsip.conf
```

Add or update transport section:
```ini
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0:7443
external_media_address=34.26.59.14
external_signaling_address=34.26.59.14
```

### 3.3 Configure WebRTC Endpoint for Your Extension

Edit `/etc/asterisk/pjsip.conf` (or via FreePBX GUI):
```ini
[2000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
allow=alaw
allow=opus
webrtc=yes
media_encryption=dtls
dtls_verify=fingerprint
dtls_setup=actpass
dtls_auto_generate_cert=yes
ice_support=yes
use_avpf=yes
media_use_received_transport=yes
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
aors=2000
auth=2000

[2000]
type=aor
max_contacts=5
remove_existing=yes

[2000]
type=auth
auth_type=userpass
username=2000
password=your_password_here
```

### 3.4 Reload Asterisk Configuration

```bash
sudo asterisk -rx "core reload"
sudo asterisk -rx "pjsip reload"
```

---

## Step 4: Generate SSL Certificate

FreePBX WebRTC requires SSL. You have two options:

### Option A: Self-Signed Certificate (Quick Testing)

```bash
# SSH into FreePBX
cd /etc/asterisk/keys

# Generate self-signed certificate
sudo openssl req -x509 -newkey rsa:4096 -keyout asterisk.key -out asterisk.pem -days 365 -nodes -subj "/CN=34.26.59.14"

# Set permissions
sudo chown asterisk:asterisk asterisk.*
sudo chmod 400 asterisk.key

# Restart Asterisk
sudo asterisk -rx "core restart now"
```

**Note:** Self-signed certificates will show browser warnings. You'll need to accept the certificate manually.

### Option B: Let's Encrypt Certificate (Production)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install -y certbot

# Get certificate (requires domain name, not just IP)
# If you have a domain pointing to 34.26.59.14:
sudo certbot certonly --standalone -d your-domain.com

# Link certificates to Asterisk
sudo ln -sf /etc/letsencrypt/live/your-domain.com/fullchain.pem /etc/asterisk/keys/asterisk.pem
sudo ln -sf /etc/letsencrypt/live/your-domain.com/privkey.pem /etc/asterisk/keys/asterisk.key
sudo chown -R asterisk:asterisk /etc/asterisk/keys/

# Restart Asterisk
sudo asterisk -rx "core restart now"
```

---

## Step 5: Configure Your Call Center Application

Update `call_center/config.py`:

```python
SIP_CONFIG = {
    'domain': '34.26.59.14',  # Your FreePBX IP
    'wss_port': 7443,         # WebSocket Secure port
    'transport': 'wss',       # Use WSS (secure)
    
    # STUN server for NAT traversal
    'ice_servers': [
        {
            'urls': 'stun:stun.l.google.com:19302'
        }
    ]
}
```

---

## Step 6: Test WebRTC Connection

### 6.1 Test WSS Port is Open

```bash
# From your local machine
telnet 34.26.59.14 7443

# Or use openssl to test SSL
openssl s_client -connect 34.26.59.14:7443

# Should show SSL certificate and connection
```

### 6.2 Test in Browser

Open browser console (F12) and try connecting:

```javascript
// Test WebSocket connection
let ws = new WebSocket('wss://34.26.59.14:7443');
ws.onopen = () => console.log('Connected!');
ws.onerror = (err) => console.error('Error:', err);
```

### 6.3 Access Call Center Interface

```
https://your-domain.com/call-center/

Login with:
- Extension: 2000
- Username: 2000
- Password: your_password_here
```

---

## Step 7: Accept Self-Signed Certificate (If Using)

If using self-signed certificate, you must accept it first:

1. Open in browser: `https://34.26.59.14:8089`
2. You'll see security warning
3. Click "Advanced" → "Proceed anyway"
4. Now try: `wss://34.26.59.14:7443`
5. Accept certificate again if prompted

---

## Common Issues & Solutions

### Issue 1: "Failed to connect to WSS"

**Symptoms:**
- Browser console: `WebSocket connection to 'wss://34.26.59.14:7443' failed`
- Network error or timeout

**Causes & Fixes:**

1. **Google Cloud firewall blocking port 7443**
   ```bash
   # Check if firewall rule exists
   gcloud compute firewall-rules list | grep 7443
   
   # If missing, create it (see Step 2)
   ```

2. **FreePBX firewall blocking WSS**
   ```bash
   # SSH into FreePBX
   sudo fwconsole firewall disable  # Temporarily for testing
   
   # Or add port 7443 to allowed ports
   ```

3. **Asterisk not listening on 7443**
   ```bash
   # Check if Asterisk is listening
   sudo netstat -tlnp | grep 7443
   
   # Should show: tcp  0.0.0.0:7443  0.0.0.0:*  LISTEN  12345/asterisk
   
   # If not, check http.conf and pjsip.conf configuration
   ```

### Issue 2: "SSL Certificate Error"

**Symptoms:**
- Browser blocks connection due to invalid certificate
- Console: `net::ERR_CERT_AUTHORITY_INVALID`

**Solution:**
- Manually accept self-signed certificate (see Step 7)
- Or use Let's Encrypt certificate (Option B in Step 4)

### Issue 3: "Connection drops immediately"

**Symptoms:**
- Connects briefly then disconnects
- "Connection closed" in console

**Causes:**
1. **Wrong SIP credentials**
   - Verify username/password for extension 2000
   - Check in FreePBX: Applications → Extensions → 2000

2. **WebRTC not enabled for extension**
   - Edit extension in FreePBX
   - Advanced → Enable WebRTC: Yes
   - Apply config

3. **PJSIP transport misconfigured**
   - Check pjsip.conf has transport-wss section
   - Reload: `asterisk -rx "pjsip reload"`

### Issue 4: "Connected but no audio"

**Symptoms:**
- SIP registration succeeds
- Calls connect but no audio in either direction

**Causes & Fixes:**

1. **RTP ports not open**
   ```bash
   # Add Google Cloud firewall rule for RTP
   gcloud compute firewall-rules create allow-rtp \
       --direction=INGRESS \
       --action=ALLOW \
       --rules=udp:10000-20000 \
       --source-ranges=0.0.0.0/0
   ```

2. **STUN server not configured**
   - Update call_center/config.py with STUN server (see Step 5)

3. **Browser microphone permissions**
   - Check browser allowed microphone access
   - Look for microphone icon in address bar

4. **NAT/external IP issues**
   - Verify external_media_address in pjsip.conf: 34.26.59.14
   - Not internal IP (10.x.x.x)

### Issue 5: "Authentication Failed"

**Symptoms:**
- "403 Forbidden" or "401 Unauthorized"
- SIP registration fails

**Solution:**
```bash
# Check extension exists
asterisk -rx "pjsip show endpoints" | grep 2000

# Verify auth credentials match
# FreePBX → Applications → Extensions → 2000
# Username and password must match config

# Check Asterisk logs
tail -f /var/log/asterisk/full | grep 2000
```

---

## Debug Commands

### Check Asterisk Status
```bash
sudo asterisk -rx "core show version"
sudo asterisk -rx "http show status"
sudo asterisk -rx "pjsip show transports"
sudo asterisk -rx "pjsip show endpoints"
```

### Enable Debug Logging
```bash
# Enable PJSIP debug
sudo asterisk -rx "pjsip set logger on"

# Watch logs
sudo tail -f /var/log/asterisk/full | grep -E "PJSIP|WebSocket|2000"
```

### Test Port Connectivity
```bash
# Test from local machine
nc -zv 34.26.59.14 7443
nmap -p 7443 34.26.59.14

# Test SSL handshake
openssl s_client -connect 34.26.59.14:7443 -showcerts
```

---

## Quick Checklist

- [ ] Google Cloud firewall allows TCP 7443
- [ ] Google Cloud firewall allows UDP 10000-20000 (RTP)
- [ ] FreePBX firewall allows WSS traffic
- [ ] Asterisk http.conf configured for WSS
- [ ] PJSIP transport-wss configured
- [ ] Extension 2000 exists and has WebRTC enabled
- [ ] SSL certificate generated and configured
- [ ] External IP (34.26.59.14) used in all configs, not internal IP
- [ ] STUN server configured in call_center/config.py
- [ ] Port 7443 is open and listening
- [ ] Browser has microphone permissions
- [ ] Self-signed certificate accepted in browser (if using)

---

## Complete Configuration Files

### /etc/asterisk/http.conf
```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
tlsenable=yes
tlsbindaddr=0.0.0.0:8089
tlscertfile=/etc/asterisk/keys/asterisk.pem
tlsprivatekey=/etc/asterisk/keys/asterisk.key
```

### /etc/asterisk/pjsip.conf (relevant sections)
```ini
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0:7443
external_media_address=34.26.59.14
external_signaling_address=34.26.59.14

[2000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
allow=opus
webrtc=yes
media_encryption=dtls
dtls_verify=fingerprint
ice_support=yes
use_avpf=yes
rtp_symmetric=yes
force_rport=yes
aors=2000
auth=2000

[2000]
type=aor
max_contacts=5

[2000]
type=auth
auth_type=userpass
username=2000
password=your_strong_password
```

---

## Alternative: Using WebRTC Phone Outside Your App

If you just want to test WebRTC connectivity:

### Option 1: Use JsSIP Demo
```
https://tryit.jssip.net/

Settings:
- SIP URI: sip:2000@34.26.59.14
- SIP Password: your_password
- WebSocket URI: wss://34.26.59.14:7443
```

### Option 2: Use MicroSIP
Download MicroSIP and configure:
- Account: 2000
- Domain: 34.26.59.14
- Password: your_password
- Transport: WSS
- Server: 34.26.59.14:7443

---

## Summary

**For WebRTC to work on Google Cloud FreePBX:**

1. ✅ Open TCP port 7443 in Google Cloud firewall
2. ✅ Configure WebSocket in Asterisk (http.conf, pjsip.conf)
3. ✅ Generate SSL certificate
4. ✅ Enable WebRTC on extensions
5. ✅ Use external IP (34.26.59.14) in all configs
6. ✅ Configure STUN server
7. ✅ Accept SSL certificate in browser (if self-signed)

The issue is likely one of these not being configured properly. Start with Step 1 (firewall) and work through each step!

