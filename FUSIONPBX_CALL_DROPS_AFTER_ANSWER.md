# Fix Call Drops After Agent Answers (CALL_REJECTED)

## 🔴 Problem: Call Transfers Successfully, But Drops When Agent Answers

**Symptoms:**
- ✅ Twilio call connects to voice agent
- ✅ Call transfers to extension 2001
- ✅ Extension 2001 rings
- ❌ Call drops immediately when agent answers
- ❌ Logs show: `CALL_REJECTED` on extension 2001 leg

**Example Log:**
```
[NOTICE] sofia.c:8736 Hangup sofia/internal/2001@198.27.217.12:55965 [CS_CONSUME_MEDIA] [CALL_REJECTED]
[NOTICE] switch_cpp.cpp:752 Hangup sofia/internal/+19259897818@sip.twilio.com [CS_EXECUTE] [NORMAL_CLEARING]
```

## 🔍 Root Causes

The `CALL_REJECTED` error with `CS_CONSUME_MEDIA` typically indicates:

1. **Media (RTP) Negotiation Failure** - Most common
   - Codec mismatch between Twilio and agent's phone
   - RTP ports blocked by firewall
   - NAT traversal issues
   - Incorrect RTP IP addresses

2. **Agent's Phone Rejecting Call**
   - Phone client configuration issue
   - Network connectivity problem from agent's device
   - Codec not supported by agent's phone

3. **FreeSWITCH Media Handling**
   - Media bypass/disabling issues
   - Incorrect media mode settings

## ✅ Diagnostic Steps

### Step 1: Check Media Negotiation in Logs

```bash
# Watch logs during transfer and answer
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "rtp|media|codec|2001|reject"

# Look for:
# - "RTP Statistics" or "Media Statistics"
# - Codec negotiation messages
# - RTP port assignments
# - Media stream creation/teardown
```

**What to look for:**
- RTP ports being assigned
- Codec negotiation (should see PCMU or PCMA)
- Any "reject" or "decline" messages
- Media stream establishment messages

### Step 2: Enable Detailed Media Debugging

```bash
# Enable RTP debugging
fs_cli -x "console loglevel debug"

# Enable SOFIA (SIP) debugging
fs_cli -x "sofia loglevel all 9"

# Watch logs
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "rtp|media|codec|2001"
```

### Step 3: Check Codec Compatibility

```bash
# Check what codecs Twilio leg supports
fs_cli -x "sofia status profile external" | grep -i "codec"

# Check what codecs extension 2001 supports
fs_cli -x "user_data 2001@136.115.41.45 var" | grep -i "codec"

# Check what codecs are negotiated for the call
# (Run this while call is active, before it drops)
fs_cli -x "show channels" | grep -A 10 "2001"
```

**Expected:** Both should support PCMU (G.711 μ-law) or PCMA (G.711 A-law)

### Step 4: Check RTP IP Addresses

```bash
# Check external SIP profile RTP settings
fs_cli -x "sofia xmlstatus profile external" | grep -i "rtp"

# Verify external RTP IP is correct
fs_cli -x "sofia xmlstatus profile external" | grep -E "ext-rtp-ip|rtp-ip"
```

**Should show:**
- `ext-rtp-ip`: `136.115.41.45` (public IP)
- `rtp-ip`: `10.128.0.8` (internal IP)

### Step 5: Test Internal Call (Extension to Extension)

```bash
# Test if extension 2001 can make/receive internal calls
fs_cli -x "originate user/2002@136.115.41.45 &echo()"

# Then have extension 2002 call 2001
fs_cli -x "originate user/2001@136.115.41.45 &echo()"
```

**If internal calls work but Twilio transfers don't:** The issue is with Twilio ↔ FusionPBX media path, not the extension itself.

### Step 6: Check Firewall Rules for RTP

```bash
# Check if RTP ports (10000-20000) are open
netstat -tuln | grep -E ":(10[0-9]{3}|1[1-9][0-9]{3}|20000)"

# Or use iptables
iptables -L -n | grep -E "5060|10000:20000"
```

**RTP uses UDP ports 10000-20000.** These must be open for media to flow.

### Step 7: Check Agent's Phone Configuration

Ask the agent to check their SIP phone settings:

1. **Codec Settings:**
   - Ensure PCMU (G.711 μ-law) or PCMA (G.711 A-law) is enabled
   - Disable video codecs if enabled

2. **NAT Settings:**
   - Enable "NAT Traversal" or "STUN"
   - Set "STUN Server" to: `stun:stun.l.google.com:19302`

3. **Network:**
   - Check if phone can reach FusionPBX IP `136.115.41.45`
   - Test from agent's network: `telnet 136.115.41.45 5060`

### Step 8: Check Media Mode in FreeSWITCH

```bash
# Check media mode for extension 2001
fs_cli -x "user_data 2001@136.115.41.45 var" | grep -i "media"

# Check if media bypass is enabled (should be disabled for Twilio)
fs_cli -x "sofia xmlstatus profile external" | grep -i "bypass"
```

## 🔧 Solutions

### Solution 1: Fix Codec Mismatch (Most Common)

**Force PCMU/PCMA on External Profile:**

1. **Via FusionPBX GUI:**
   ```
   Advanced → SIP Profiles → external → Edit
   → Settings tab
   → Find "Codec Preferences"
   → Set:
       Inbound Codec Preferences: PCMU,PCMA
       Outbound Codec Preferences: PCMU,PCMA
   → Save → Apply Config
   ```

2. **Via CLI (edit `/etc/freeswitch/sip_profiles/external.xml`):**
   ```xml
   <param name="inbound-codec-prefs" value="PCMU,PCMA"/>
   <param name="outbound-codec-prefs" value="PCMU,PCMA"/>
   ```

3. **Reload SIP Profile:**
   ```bash
   fs_cli -x "reload mod_sofia"
   # Or via FusionPBX GUI: Status → SIP Status → external → Reload XML → Restart
   ```

### Solution 2: Fix RTP IP Addresses

**Ensure External Profile Advertises Correct Public IP:**

1. **Check `/etc/freeswitch/sip_profiles/external.xml`:**
   ```xml
   <param name="ext-sip-ip" value="136.115.41.45"/>
   <param name="ext-rtp-ip" value="136.115.41.45"/>
   <param name="sip-force-contact" value="136.115.41.45:5060"/>
   <param name="rtp-force-contact" value="136.115.41.45"/>
   ```

2. **Reload:**
   ```bash
   fs_cli -x "reload mod_sofia"
   ```

### Solution 3: Open Firewall Ports for RTP

```bash
# Open RTP port range (UDP 10000-20000)
ufw allow 10000:20000/udp

# Or with iptables
iptables -A INPUT -p udp --dport 10000:20000 -j ACCEPT
iptables-save

# Also ensure SIP port is open
ufw allow 5060/udp
ufw allow 5060/tcp
```

### Solution 4: Disable Media Bypass

Media bypass can cause issues with Twilio transfers:

```bash
# Check current setting
fs_cli -x "sofia xmlstatus profile external" | grep -i "bypass"

# Edit `/etc/freeswitch/sip_profiles/external.xml`
# Ensure these are set:
<param name="bypass-media" value="false"/>
<param name="media-bypass" value="false"/>

# Reload
fs_cli -x "reload mod_sofia"
```

### Solution 5: Configure NAT Traversal

```xml
<!-- In external.xml -->
<param name="aggressive-nat-detection" value="true"/>
<param name="local-network-acl" value="localnet.auto"/>
<param name="apply-nat-acl" value="nat.auto"/>
<param name="rtp-ip" value="10.128.0.8"/>
<param name="ext-rtp-ip" value="136.115.41.45"/>
```

### Solution 6: Check Extension 2001's Media Settings

1. **Via FusionPBX GUI:**
   ```
   Accounts → Extensions → 2001 → Advanced tab
   → Check "Codec" settings
   → Ensure PCMU or PCMA is selected
   → Save
   ```

2. **Check Extension's Domain:**
   ```
   Accounts → Extensions → 2001 → Advanced tab
   → Ensure "Domain" is set to: 136.115.41.45 (or your domain)
   ```

### Solution 7: Test with Direct SIP Call

Test if the issue is specific to Twilio transfers:

```bash
# From another SIP client, make a direct call to extension 2001
# Using sip:2001@136.115.41.45:5060

# If this works, the issue is Twilio-specific
# If this also drops, the issue is with extension 2001 or FusionPBX configuration
```

## 📊 Detailed Log Analysis

When reviewing logs, look for these specific patterns:

### Good Signs (Call Should Work):
```
[NOTICE] sofia.c:xxxx Channel [sofia/internal/2001@...] has been answered
[DEBUG] switch_rtp.c:xxxx RTP Server Ready [external IP:136.115.41.45:xxxx]
[DEBUG] switch_rtp.c:xxxx Starting timer [soft] 160 bytes [60]ms
[INFO] switch_core_media.c:xxxx Media Codec [PCMU] Negotiation Complete
```

### Bad Signs (Call Will Drop):
```
[WARNING] sofia.c:xxxx Failed to establish RTP stream
[ERROR] switch_rtp.c:xxxx RTP timeout waiting for media
[NOTICE] sofia.c:xxxx Hangup sofia/internal/2001@... [CS_CONSUME_MEDIA] [CALL_REJECTED]
[WARNING] switch_core_media.c:xxxx Codec negotiation failed
```

## 🎯 Quick Fix Checklist

Run through these in order:

- [ ] **Codec mismatch:** Force PCMU/PCMA on external profile
- [ ] **RTP IPs:** Verify `ext-rtp-ip` is `136.115.41.45`
- [ ] **Firewall:** Open UDP ports 10000-20000
- [ ] **Media bypass:** Disable media bypass on external profile
- [ ] **Extension codec:** Ensure extension 2001 supports PCMU/PCMA
- [ ] **NAT settings:** Enable aggressive NAT detection
- [ ] **Test internal:** Verify extension 2001 works for internal calls
- [ ] **Agent phone:** Check agent's SIP phone codec and NAT settings

## 🔍 Still Not Working?

If the call still drops after trying all solutions:

1. **Capture Full SIP Trace:**
   ```bash
   fs_cli -x "sofia loglevel all 9"
   # Attempt transfer and capture full output
   tail -f /var/log/freeswitch/freeswitch.log > /tmp/sip_trace.log
   ```

2. **Check Twilio Call Logs:**
   - Go to Twilio Console → Monitor → Logs → Calls
   - Find the failed transfer call
   - Check "Media Streams" section
   - Look for RTP/STUN errors

3. **Test with Different Extension:**
   ```bash
   # Try transferring to extension 2002
   # If 2002 works, the issue is specific to extension 2001
   ```

4. **Check FreeSWITCH Version:**
   ```bash
   freeswitch -version
   # Older versions may have media handling bugs
   ```

## 📝 Summary

The most common cause of `CALL_REJECTED` after answer is **media negotiation failure**. Focus on:

1. **Codec compatibility** (PCMU/PCMA)
2. **RTP IP addresses** (must advertise public IP)
3. **Firewall rules** (RTP ports 10000-20000 UDP)
4. **NAT traversal** (aggressive NAT detection)

Start with Solution 1 (codec mismatch) as it's the most common issue.
