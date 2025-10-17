# WebSocket Port Configuration Guide

## ❓ Why Port 7443 Instead of 443?

### **Standard Port Usage:**

| Port | Service | Notes |
|------|---------|-------|
| **443** | HTTPS Web Server | Apache/Nginx serving FreePBX web UI |
| **7443** | Asterisk WSS | **Default for FreePBX WebRTC** |
| **8089** | FreePBX HTTPS | Alternative admin interface |
| **5060** | SIP (UDP) | Non-secure SIP signaling |
| **5061** | SIP-TLS (TCP) | Secure SIP signaling |
| **8088** | Asterisk HTTP | Non-secure HTTP (not recommended) |

### **Why 7443?**

1. **Port 443 is occupied**: Your web server (Apache/Nginx) already uses it for the FreePBX admin interface
2. **Asterisk convention**: 7443 is the standard Asterisk/FreePBX port for WebSocket Secure (WSS)
3. **No conflicts**: Separates web traffic (443) from WebRTC traffic (7443)

---

## 🔧 How Port Configuration Works Now

### **Before (Hardcoded):**
```javascript
// ❌ Port was hardcoded in JavaScript
const socket = new JsSIP.WebSocketInterface(`wss://${domain}:7443`);
```

### **After (Configurable):**

**1. Configure in `call_center/config.py`:**
```python
SIP_CONFIG = {
    'domain': '34.26.59.14',
    'wss_port': 7443,  # ← Change this!
}
```

**2. JavaScript reads from config:**
```javascript
// ✓ Port comes from server config
const wssPort = window.SIP_CONFIG.wss_port;  // → 7443
const socket = new JsSIP.WebSocketInterface(`wss://${domain}:${wssPort}`);
```

---

## 📋 Port Options

### **Option 1: Use 7443 (Recommended - Default)**

**Advantages:**
- ✅ Asterisk/FreePBX default
- ✅ No web server conflicts
- ✅ Standard convention

**Configuration:**
```python
SIP_CONFIG = {
    'domain': '34.26.59.14',
    'wss_port': 7443
}
```

**FreePBX Setup:**
```ini
# /etc/asterisk/pjsip.conf
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0:7443
```

**Firewall:**
```bash
# Google Cloud
gcloud compute firewall-rules create allow-wss \
    --allow=tcp:7443

# Or UFW
sudo ufw allow 7443/tcp
```

---

### **Option 2: Use 8089 (Alternative)**

**Advantages:**
- ✅ FreePBX also listens here
- ✅ Same certificate as admin interface
- ✅ May already be open

**Configuration:**
```python
SIP_CONFIG = {
    'domain': '34.26.59.14',
    'wss_port': 8089
}
```

**FreePBX Setup:**
```ini
# Already configured in /etc/asterisk/http.conf
tlsbindaddr=0.0.0.0:8089
```

**Note:** This shares the port with FreePBX admin HTTPS interface.

---

### **Option 3: Use 443 (Requires Reverse Proxy)**

**Advantages:**
- ✅ Standard HTTPS port
- ✅ Better firewall compatibility
- ✅ No special port needed

**Disadvantages:**
- ❌ Requires Nginx/Apache reverse proxy
- ❌ More complex setup
- ❌ Port conflict with web server

**Configuration:**

**1. Update config:**
```python
SIP_CONFIG = {
    'domain': '34.26.59.14',
    'wss_port': 443
}
```

**2. Setup Nginx reverse proxy:**
```nginx
# /etc/nginx/sites-available/freepbx-wss
server {
    listen 443 ssl;
    server_name 34.26.59.14;
    
    ssl_certificate /etc/asterisk/keys/asterisk.pem;
    ssl_certificate_key /etc/asterisk/keys/asterisk.key;
    
    # Proxy WebSocket connections
    location /ws {
        proxy_pass https://127.0.0.1:7443;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    # Regular HTTPS for admin
    location / {
        proxy_pass http://127.0.0.1:80;
    }
}
```

**3. Update JavaScript to use /ws path:**
```javascript
const socket = new JsSIP.WebSocketInterface(`wss://${domain}/ws`);
```

---

## 🎯 Which Port Should You Use?

### **For Testing/Development:**
→ **Use 7443** (simplest, default)

### **For Production:**
→ **Use 7443** (still recommended) or **443 with reverse proxy** (if you need standard port)

### **Quick Setup:**
→ **Use 8089** (if 7443 not working and you don't want to configure)

---

## 🔧 How to Change the Port

### **Step 1: Update Configuration**

Edit `/Users/hj/Web Development Projects/1. Main/call_center/config.py`:
```python
SIP_CONFIG = {
    'domain': '34.26.59.14',
    'wss_port': 8089,  # Changed from 7443 to 8089
}
```

### **Step 2: Configure FreePBX for That Port**

**For 7443:**
```ini
# /etc/asterisk/pjsip.conf
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0:7443
```

**For 8089:**
```ini
# Already in /etc/asterisk/http.conf
tlsenable=yes
tlsbindaddr=0.0.0.0:8089
```

### **Step 3: Open Firewall**

```bash
# Google Cloud
gcloud compute firewall-rules create allow-wss-8089 \
    --allow=tcp:8089

# On FreePBX VM
sudo ufw allow 8089/tcp
```

### **Step 4: Restart Services**

```bash
# Restart Flask app
python app.py

# Restart Asterisk (on FreePBX)
sudo asterisk -rx "core restart now"
```

### **Step 5: Test**

```bash
# Test port is open
telnet 34.26.59.14 8089

# Or nmap
nmap -p 8089 34.26.59.14
```

---

## 🐛 Troubleshooting

### Issue: Connection Refused

**Symptom:** `WebSocket connection to 'wss://34.26.59.14:7443/' failed`

**Causes & Fixes:**

1. **Port not open in Google Cloud firewall**
   ```bash
   gcloud compute firewall-rules list | grep 7443
   # If missing, create rule
   ```

2. **Asterisk not listening on that port**
   ```bash
   ssh root@34.26.59.14
   netstat -tlnp | grep 7443
   # Should show asterisk listening
   ```

3. **Wrong port in configuration**
   - Check `config.py` has correct port
   - Check FreePBX is configured for that port

### Issue: SSL Certificate Error

**Symptom:** Certificate warning or connection blocked

**Solution:**
1. Accept self-signed certificate manually
2. Or use Let's Encrypt certificate (production)

### Issue: Port Already in Use

**Symptom:** Asterisk won't start, port conflict error

**Solution:**
```bash
# Find what's using the port
sudo lsof -i :7443

# Kill process or use different port
```

---

## 📊 Port Decision Flowchart

```
Do you have Nginx/Apache reverse proxy?
  │
  ├─ YES → Use port 443 with reverse proxy
  │
  └─ NO → Is port 7443 available?
            │
            ├─ YES → Use 7443 (recommended)
            │
            └─ NO → Is port 8089 configured?
                      │
                      ├─ YES → Use 8089
                      │
                      └─ NO → Configure 7443 or use custom port
```

---

## 🎓 Summary

**The port configuration comes from:**
1. ✅ **`call_center/config.py`** - Server-side config
2. ✅ **Passed to HTML template** via Flask
3. ✅ **Read by JavaScript** via `window.SIP_CONFIG`
4. ✅ **Used by JsSIP** to connect to FreePBX

**Current setup:** Port **7443** (Asterisk/FreePBX default)

**To change:** Edit `config.py` → restart app → configure FreePBX → open firewall

**Recommended:** Stick with **7443** unless you have specific requirements!

