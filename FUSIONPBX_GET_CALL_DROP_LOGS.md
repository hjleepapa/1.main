# Get FusionPBX Logs for Call Drops When Answering

## 🔍 Problem
- ✅ Call dials and rings (registration working)
- ❌ Call drops immediately when answered

## 📋 Quick Commands to Get Logs

### Method 1: Real-Time Monitoring (Recommended)

Enable maximum logging and watch in real-time, then make the call:

```bash
# Enable maximum logging
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Watch logs in real-time - make the call now!
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2001|2003|answer|bridge|media|rtp|codec|hangup|486|603|decline|reject|failed"
```

### Method 2: Capture Full Call Flow

Get logs for the specific call after it happens:

```bash
# Get recent logs with extensions 2001 and 2003
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "2001|2003" | tail -100

# Get logs with answer/bridge/hangup events
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "answer|bridge|hangup|2001|2003" | tail -100
```

### Method 3: Get Call-Specific Logs by Call UUID

1. First, get the call UUID from recent logs:
```bash
# Find the most recent call UUID involving 2001 and 2003
tail -200 /var/log/freeswitch/freeswitch.log | grep -E "New Channel.*2001|New Channel.*2003" | tail -1
```

2. Then get all logs for that call:
```bash
# Replace CALL_UUID with the actual UUID from step 1
grep "CALL_UUID" /var/log/freeswitch/freeswitch.log | tail -200
```

### Method 4: Get Logs with Context (Before/After Answer)

Get logs showing what happens right before and after answering:

```bash
# Get logs with 5 lines before and after matches
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "2001|2003" -A 5 -B 5 | tail -150

# Focus on answer/bridge events
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "answer|bridge|hangup" -A 10 -B 10 | grep -iE "2001|2003" | tail -100
```

## 🎯 Specific Log Searches

### 1. Look for Answer Events

```bash
# Look for answer/bridge events
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "ANSWER|CHANNEL_ANSWER|bridge.*2003" | tail -30
```

### 2. Look for Media/RTP Issues

```bash
# Look for RTP and media negotiation issues
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "rtp|media|codec|sdp|ice" | grep -iE "2001|2003" | tail -50
```

### 3. Look for Hangup/Call End Reasons

```bash
# Look for hangup causes
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "hangup|HANGUP|terminated|NORMAL|CALL_REJECTED|486|603" | grep -iE "2001|2003" | tail -30
```

### 4. Look for SIP Response Codes

```bash
# Look for SIP error codes
tail -500 /var/log/freeswitch/freeswitch.log | grep -E "SIP/2.0 [4-6][0-9][0-9]|^[0-9]{3} " | grep -iE "2001|2003" | tail -30
```

### 5. Look for Bridge Failures

```bash
# Look for bridge or media bridge failures
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "bridge.*fail|media.*fail|unable.*bridge" | grep -iE "2001|2003" | tail -30
```

## 📊 Complete Diagnostic Command

Run this to capture everything in real-time:

```bash
# Step 1: Clear previous logs (optional - be careful!)
# tail -0 /var/log/freeswitch/freeswitch.log > /dev/null

# Step 2: Enable maximum logging
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Step 3: Start monitoring in real-time
tail -f /var/log/freeswitch/freeswitch.log | tee /tmp/call_log_$(date +%Y%m%d_%H%M%S).txt | grep -iE "2001|2003|answer|bridge|media|rtp|codec|hangup|486|603|decline|reject|failed|error|SIP/2.0"
```

**Then:**
1. Make the call from 2001 to 2003
2. Let it ring
3. Answer on 2003
4. Watch the logs as it drops
5. Stop with `Ctrl+C`
6. The full log will be saved to `/tmp/call_log_*.txt`

## 🔍 Most Important Log Sections to Check

After getting the logs, look for these specific patterns:

### 1. Answer Event
```
CHANNEL_ANSWER|CHANNEL_EXECUTE.*answer|answered
```

### 2. Media Negotiation
```
SDP|codec|RTP|media-bypass|bypass-media
```

### 3. RTP Setup
```
Starting RTP|RTP|RTCP|UDP port|media.*start
```

### 4. Hangup Cause
```
HANGUP|hangup_cause|NORMAL_CLEARING|CALL_REJECTED|486|603
```

### 5. Bridge Status
```
Bridge|bridge.*2003|unable.*bridge|bridge.*fail
```

## 📋 Extract Logs by Time Range

If you know approximately when the call happened:

```bash
# Get logs from last 10 minutes
tail -n +$(($(wc -l < /var/log/freeswitch/freeswitch.log) - 5000)) /var/log/freeswitch/freeswitch.log | grep -iE "2001|2003" | tail -100

# Or use journalctl if using systemd (alternative log location)
journalctl -u freeswitch -n 500 --no-pager | grep -iE "2001|2003"
```

## 🎯 Quick One-Liner for Immediate Log Capture

Run this command, then make the call:

```bash
fs_cli -x "sofia loglevel all 9" && fs_cli -x "console loglevel debug" && echo "Logging enabled. Make your call now..." && tail -f /var/log/freeswitch/freeswitch.log | grep --line-buffered -iE "2001|2003|answer|bridge|hangup|486|603|rtp|media|codec"
```

## 📝 Save Logs to File

To save logs to a file for later analysis:

```bash
# Save to file with timestamp
LOG_FILE="/tmp/fusionpbx_call_drop_$(date +%Y%m%d_%H%M%S).log"

# Enable logging and save
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Start capturing
tail -f /var/log/freeswitch/freeswitch.log | tee "$LOG_FILE" | grep -iE "2001|2003"
```

After the call, check the file:
```bash
cat "$LOG_FILE" | grep -iE "answer|bridge|hangup|486|603|rtp|media"
```

## 🔍 Common Issues to Look For

Based on the symptoms (drops when answered), check for:

1. **Codec Mismatch:**
   ```bash
   tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "codec|no.*codec|codec.*fail" | grep -iE "2001|2003"
   ```

2. **RTP Port Issues:**
   ```bash
   tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "RTP|rtp.*port|UDP.*port" | grep -iE "2001|2003"
   ```

3. **Media Bypass Issues:**
   ```bash
   tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "bypass.*media|media.*bypass" | grep -iE "2001|2003"
   ```

4. **SIP Reject (486/603):**
   ```bash
   tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "486|603|Busy|Decline" | grep -iE "2001|2003"
   ```

## ✅ Next Steps

1. **Run the real-time monitoring command** above
2. **Make the call** from 2001 to 2003
3. **Answer on 2003** and watch the logs
4. **Share the logs** showing what happens when you answer
5. Look specifically for:
   - Answer events
   - Media negotiation
   - RTP setup
   - Hangup causes

This will help identify why the call drops when answered!
