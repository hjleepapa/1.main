# FreePBX on Google Cloud VM - Call Transfer Setup

## Your Setup

- **FreePBX IP**: `34.26.59.14` (Google Cloud VM external IP)
- **Twilio Inbound**: `+12344007818`
- **Twilio Trunk**: `+19256337818`
- **Target Extension**: `2000`

## Critical: Google Cloud Firewall Configuration

Google Cloud requires **TWO layers of firewall rules**:
1. **Google Cloud Firewall** (VPC Network level)
2. **FreePBX Firewall** (OS level on the VM)

Both must be configured for Twilio → FreePBX SIP traffic to work.

---

## Step 1: Configure Google Cloud Firewall Rules

### 1.1 Create Firewall Rule for SIP (Port 5060/UDP)

```bash
# Via Google Cloud Console:
Go to: VPC Network → Firewall → Create Firewall Rule

Name: allow-twilio-sip
Description: Allow Twilio SIP traffic to FreePBX
Direction: Ingress
Action on match: Allow
Targets: Specified target tags or "All instances in network"
Target tags: freepbx (or your VM's network tag)
Source filter: IP ranges
Source IP ranges:
  54.172.60.0/23
  54.244.51.0/24
  177.71.206.192/26
  54.252.254.64/26
  54.169.127.128/26
Protocols and ports: UDP: 5060

Click: Create
```

### 1.2 Create Firewall Rule for RTP (Ports 10000-20000/UDP)

```bash
# Via Google Cloud Console:
VPC Network → Firewall → Create Firewall Rule

Name: allow-twilio-rtp
Description: Allow Twilio RTP/media traffic to FreePBX
Direction: Ingress
Action on match: Allow
Targets: Specified target tags or "All instances in network"
Target tags: freepbx (or your VM's network tag)
Source filter: IP ranges
Source IP ranges:
  54.172.60.0/23
  54.244.51.0/24
  177.71.206.192/26
  54.252.254.64/26
  54.169.127.128/26
Protocols and ports: UDP: 10000-20000

Click: Create
```

### 1.3 Using gcloud CLI (Alternative)

```bash
# Create SIP firewall rule
gcloud compute firewall-rules create allow-twilio-sip \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=udp:5060 \
    --source-ranges=54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26 \
    --target-tags=freepbx

# Create RTP firewall rule
gcloud compute firewall-rules create allow-twilio-rtp \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=udp:10000-20000 \
    --source-ranges=54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26 \
    --target-tags=freepbx
```

---

## Step 2: Configure FreePBX Firewall (VM Level)

### 2.1 SSH into Your FreePBX VM

```bash
# From local machine or Google Cloud Console SSH
gcloud compute ssh freepbx-instance --zone=your-zone

# Or use Google Cloud Console → Compute Engine → VM instances → SSH
```

### 2.2 Option A: Add Twilio IPs to FreePBX Responsive Firewall

```bash
# Via FreePBX Web GUI:
Log into FreePBX: http://34.26.59.14

Admin → System Admin → Firewall

Under "Networks" tab:
  Click "Add Network"
  
  Add each Twilio IP range:
  54.172.60.0/23 - Description: Twilio SIP 1
  54.244.51.0/24 - Description: Twilio SIP 2
  177.71.206.192/26 - Description: Twilio SIP 3
  54.252.254.64/26 - Description: Twilio SIP 4
  54.169.127.128/26 - Description: Twilio SIP 5
  
  Zone: Trusted
  
Click: Submit and Apply Config
```

### 2.2 Option B: Configure iptables Directly

```bash
# SSH into FreePBX VM
sudo -i

# Add Twilio IPs to iptables
iptables -I INPUT -p udp --dport 5060 -s 54.172.60.0/23 -j ACCEPT
iptables -I INPUT -p udp --dport 5060 -s 54.244.51.0/24 -j ACCEPT
iptables -I INPUT -p udp --dport 5060 -s 177.71.206.192/26 -j ACCEPT
iptables -I INPUT -p udp --dport 5060 -s 54.252.254.64/26 -j ACCEPT
iptables -I INPUT -p udp --dport 5060 -s 54.169.127.128/26 -j ACCEPT

# Add RTP ports
iptables -I INPUT -p udp --dport 10000:20000 -s 54.172.60.0/23 -j ACCEPT
iptables -I INPUT -p udp --dport 10000:20000 -s 54.244.51.0/24 -j ACCEPT
iptables -I INPUT -p udp --dport 10000:20000 -s 177.71.206.192/26 -j ACCEPT
iptables -I INPUT -p udp --dport 10000:20000 -s 54.252.254.64/26 -j ACCEPT
iptables -I INPUT -p udp --dport 10000:20000 -s 54.169.127.128/26 -j ACCEPT

# Save rules
service iptables save

# Or on newer systems:
iptables-save > /etc/iptables/rules.v4
```

### 2.3 Option C: Temporarily Disable for Testing

```bash
# SSH into FreePBX VM
sudo -i

# Temporarily disable FreePBX firewall
fwconsole firewall disable

# Or disable fail2ban
systemctl stop fail2ban

# Test transfer, then re-enable:
fwconsole firewall enable
systemctl start fail2ban
```

---

## Step 3: Configure FreePBX SIP Settings for External IP

### 3.1 Set External IP in FreePBX

```bash
# FreePBX GUI:
Settings → Asterisk SIP Settings → General SIP Settings

NAT Settings:
  External Address: 34.26.59.14
  Local Network: 10.x.x.x/16 (your GCP internal network)
  
Re-detect Network Settings: Click button to auto-detect

Click: Submit and Apply Config
```

### 3.2 Configure PJSIP for External IP

```bash
# FreePBX GUI:
Settings → Asterisk SIP Settings → chan_pjsip Settings

External Media Address: 34.26.59.14
External Signaling Address: 34.26.59.14

Click: Submit and Apply Config
```

### 3.3 Verify Asterisk Configuration

```bash
# SSH into FreePBX
ssh root@34.26.59.14

# Check if Asterisk sees correct IPs
asterisk -rx "pjsip show settings" | grep external

# Should show:
# external_media_address: 34.26.59.14
# external_signaling_address: 34.26.59.14
```

---

## Step 4: Verify Network Configuration

### 4.1 Check VM Network Details

```bash
# In Google Cloud Console:
Compute Engine → VM instances → your-freepbx-vm

Check:
- External IP: 34.26.59.14 ✓
- Network: default (or your VPC)
- Network tags: freepbx (should match firewall rules)
```

### 4.2 Test Port Connectivity

```bash
# From local machine, test if SIP port is reachable:
nc -zvu 34.26.59.14 5060

# Or use nmap:
nmap -sU -p 5060 34.26.59.14

# Should show: 5060/udp open
```

### 4.3 Check FreePBX is Listening

```bash
# SSH into FreePBX VM
ssh root@34.26.59.14

# Check if Asterisk is listening on correct port
netstat -ulnp | grep 5060

# Should show:
# udp  0.0.0.0:5060  0.0.0.0:*  12345/asterisk
```

---

## Step 5: Configure Your Application

### 5.1 Update .env File

```bash
# Your .env should have:
FREEPBX_DOMAIN=34.26.59.14  # External IP, not internal IP
TRANSFER_TIMEOUT=30
```

### 5.2 Verify Application Configuration

```bash
# Check routes.py generates correct TwiML:
curl -X POST https://hjlees.com/convonet_todo/twilio/transfer \
  -d "extension=2000" \
  -d "CallSid=test" \
  -d "From=+1234567890"

# Should return:
# <Dial><Sip>sip:2000@34.26.59.14</Sip></Dial>
```

---

## Step 6: Test the Transfer

### 6.1 End-to-End Test

```
1. Call +12344007818 (your Twilio inbound number)
2. Voice AI answers
3. Say: "Transfer me to an agent"
4. Should hear: "Transferring you to an agent. Please wait."
5. Extension 2000 should ring
6. Agent answers, call is bridged
```

### 6.2 Monitor Logs During Test

**Terminal 1 - Application Logs:**
```bash
tail -f logs/app.log | grep -i transfer
```

**Terminal 2 - FreePBX Logs:**
```bash
gcloud compute ssh freepbx-instance --zone=your-zone
sudo tail -f /var/log/asterisk/full | grep -E "INVITE|2000"
```

**Terminal 3 - Google Cloud Firewall Logs (Optional):**
```bash
gcloud logging read "resource.type=gce_firewall_rule" --limit 50
```

---

## Common Issues with Google Cloud Setup

### Issue 1: "Transfer failed" - Firewall blocking

**Symptoms:**
- Transfer times out
- No activity in FreePBX logs
- No INVITE messages

**Cause:** Google Cloud firewall blocking Twilio IPs

**Solution:**
```bash
# Verify firewall rules exist:
gcloud compute firewall-rules list | grep twilio

# Check if rules are applied to your VM:
gcloud compute instances describe your-vm-name --zone=your-zone | grep tags

# Ensure VM has correct network tag
gcloud compute instances add-tags your-vm-name \
  --tags=freepbx \
  --zone=your-zone
```

### Issue 2: NAT/RTP Issues - Call connects but no audio

**Symptoms:**
- Transfer succeeds
- Agent answers
- No audio in either direction

**Cause:** RTP ports not open or NAT misconfigured

**Solution:**
```bash
# 1. Verify RTP firewall rule exists:
gcloud compute firewall-rules describe allow-twilio-rtp

# 2. Check FreePBX NAT settings:
# FreePBX GUI → Settings → Asterisk SIP Settings
# External Address: 34.26.59.14
# NAT: Yes

# 3. Enable RTP debugging:
ssh root@34.26.59.14
asterisk -rx "rtp set debug on"
# Make test call and check logs
```

### Issue 3: Internal IP vs External IP Confusion

**Symptoms:**
- FreePBX reports internal IP (10.x.x.x)
- Transfer fails with "Unable to route"

**Cause:** Using internal GCP IP instead of external IP

**Solution:**
```bash
# Always use EXTERNAL IP in your config:
FREEPBX_DOMAIN=34.26.59.14  # ✓ External IP
# NOT: 10.128.0.5             # ✗ Internal IP

# Check VM IPs:
gcloud compute instances describe your-vm-name --zone=your-zone \
  --format="get(networkInterfaces[0].networkIP,networkInterfaces[0].accessConfigs[0].natIP)"
```

### Issue 4: Fail2ban Blocking Twilio

**Symptoms:**
- First transfer works
- Subsequent transfers fail
- FreePBX logs show "Blocked by fail2ban"

**Cause:** Fail2ban sees Twilio IPs as suspicious

**Solution:**
```bash
# SSH into FreePBX
ssh root@34.26.59.14

# Add Twilio IPs to fail2ban whitelist:
vi /etc/fail2ban/jail.local

# Add under [DEFAULT]:
ignoreip = 127.0.0.1/8 54.172.60.0/23 54.244.51.0/24 177.71.206.192/26 54.252.254.64/26 54.169.127.128/26

# Restart fail2ban:
systemctl restart fail2ban

# Unban if already blocked:
fail2ban-client unban --all
```

---

## Quick Debug Checklist

- [ ] **Google Cloud firewall rules exist** for UDP 5060 and 10000-20000
- [ ] **VM has correct network tags** matching firewall rules
- [ ] **FreePBX firewall** allows Twilio IPs (or temporarily disabled)
- [ ] **External IP** (34.26.59.14) is used in config, not internal IP
- [ ] **FreePBX SIP settings** have external IP configured
- [ ] **Port 5060 is reachable** from external (test with nmap/nc)
- [ ] **Extension 2000 exists** and is registered in FreePBX
- [ ] **Application .env** has correct FREEPBX_DOMAIN=34.26.59.14
- [ ] **Fail2ban not blocking** Twilio IPs
- [ ] **Asterisk is running** and listening on 5060

---

## Test Commands Summary

```bash
# 1. Test Google Cloud firewall rules
gcloud compute firewall-rules list | grep twilio

# 2. Test port connectivity
nc -zvu 34.26.59.14 5060

# 3. Check FreePBX is listening
ssh root@34.26.59.14 "netstat -ulnp | grep 5060"

# 4. Check Asterisk status
ssh root@34.26.59.14 "asterisk -rx 'pjsip show endpoints'"

# 5. Test transfer endpoint
curl -X POST https://hjlees.com/convonet_todo/twilio/transfer -d "extension=2000"

# 6. Watch FreePBX logs during test call
ssh root@34.26.59.14 "tail -f /var/log/asterisk/full"
```

---

## Expected Working Flow

```
User calls +12344007818
    ↓
Twilio routes to Voice AI webhook
    ↓
Voice AI answers and chats
    ↓
User says "transfer me"
    ↓
App generates: <Dial><Sip>sip:2000@34.26.59.14</Sip></Dial>
    ↓
Twilio sends SIP INVITE to 34.26.59.14:5060 (from Twilio IP)
    ↓
Google Cloud firewall: ✓ Allow (rule: allow-twilio-sip)
    ↓
FreePBX firewall: ✓ Allow (Twilio IP trusted)
    ↓
Asterisk receives INVITE, routes to extension 2000
    ↓
Extension 2000 rings
    ↓
Agent answers
    ↓
RTP media flows through ports 10000-20000
    ↓
Call is bridged ✓ SUCCESS
```

---

## Final Configuration Summary

**Google Cloud Firewall:**
```
allow-twilio-sip: UDP 5060 from Twilio IPs → VM
allow-twilio-rtp: UDP 10000-20000 from Twilio IPs → VM
```

**FreePBX Configuration:**
```
External IP: 34.26.59.14
NAT: Enabled
Trusted Networks: Twilio IPs
Extension 2000: Active
```

**Application Configuration:**
```
FREEPBX_DOMAIN=34.26.59.14
TRANSFER_TIMEOUT=30
```

---

## Need More Help?

If still not working after following this guide, collect:

1. **Google Cloud firewall rules:**
   ```bash
   gcloud compute firewall-rules list --format=json > firewall-rules.json
   ```

2. **FreePBX logs:**
   ```bash
   ssh root@34.26.59.14 "tail -100 /var/log/asterisk/full" > freepbx.log
   ```

3. **Network test:**
   ```bash
   nc -zvu 34.26.59.14 5060 > connectivity-test.txt 2>&1
   ```

4. **Application transfer TwiML:**
   ```bash
   curl -X POST https://hjlees.com/convonet_todo/twilio/transfer -d "extension=2000" > twiml.xml
   ```

Share these logs for further troubleshooting!

