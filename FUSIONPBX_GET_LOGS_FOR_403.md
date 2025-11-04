# Get Logs for 403 Forbidden Error

## 🎯 Quick Commands to Get Logs

### Method 1: Watch Logs in Real-Time (Recommended)

**Before making the call:**
```bash
# Enable detailed SIP logging
fs_cli -x "sofia loglevel all 9"

# Enable console/debug logging
fs_cli -x "console loglevel debug"

# Watch logs in real-time (run this, then make the call)
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden|deny|acl|reject"
```

**Then make the call from extension 2002 to 2001, and watch the output.**

### Method 2: Save Logs to File

```bash
# Enable logging
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Save logs to file (run this, then make the call)
tail -f /var/log/freeswitch/freeswitch.log > /tmp/403_error.log 2>&1

# After the call fails, stop with Ctrl+C, then view:
cat /tmp/403_error.log | grep -iE "2002|2001|403|forbidden|deny|acl|reject"
```

### Method 3: Get Last 100 Lines of Log

```bash
# Get recent log entries
tail -100 /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden|deny"
```

### Method 4: Search Logs for Specific Timeframe

```bash
# Get logs from last 5 minutes
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden"

# Or search all logs for today
grep -iE "2002.*2001|403|forbidden" /var/log/freeswitch/freeswitch.log | tail -50
```

## 🔍 Detailed Logging Commands

### Enable Maximum Debugging

```bash
# Connect to FreeSWITCH CLI
fs_cli

# Then run these commands in fs_cli:
sofia loglevel all 9
console loglevel debug
loglevel debug

# Exit fs_cli
/exit
```

### Watch All SIP Messages

```bash
# Watch all SIP messages (very verbose)
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "sofia|sip|invite|2002|2001"
```

### Watch for ACL/Authorization Messages

```bash
# Focus on ACL and authorization messages
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "acl|deny|allow|403|forbidden|authorization|auth"
```

## 📊 What to Look For in Logs

When you get the logs, look for these patterns:

### Good Signs (Should See):
```
[INFO] sofia.c: Received SIP INVITE from 2002@...
[DEBUG] sofia.c: ACL check for IP ...: ALLOW
[INFO] mod_dialplan_xml.c: Processing 2002 -> 2001 in context ...
```

### Bad Signs (403 Forbidden Causes):
```
[WARNING] sofia.c: IP ... Denied by acl "..."
[ERROR] sofia.c: 403 Forbidden
[NOTICE] sofia.c: Rejecting INVITE from ... - ACL deny
[WARNING] sofia.c: Authentication failed for 2002@...
[ERROR] switch_ivr_originate.c: Permission denied
```

## 🎯 Complete Logging Script

Save this as a script to capture everything:

```bash
#!/bin/bash
# Save as: capture_403_logs.sh

echo "=== Starting Log Capture ==="
echo "Make a call from 2002 to 2001 now..."
echo "Press Ctrl+C when call fails to stop logging"
echo ""

# Enable logging
fs_cli -x "sofia loglevel all 9" > /dev/null 2>&1
fs_cli -x "console loglevel debug" > /dev/null 2>&1

# Capture logs
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/tmp/403_error_${TIMESTAMP}.log"

echo "Logging to: $LOG_FILE"
echo ""

tail -f /var/log/freeswitch/freeswitch.log | tee "$LOG_FILE" | grep -iE "2002|2001|403|forbidden|deny|acl|reject|sofia|invite|auth"
```

**Usage:**
```bash
chmod +x capture_403_logs.sh
./capture_403_logs.sh
# Make the call, wait for error, then Ctrl+C
# Check the log file:
cat /tmp/403_error_*.log
```

## 📋 One-Liner Commands (Copy & Paste)

### Get logs for last call attempt:
```bash
tail -200 /var/log/freeswitch/freeswitch.log | grep -A 5 -B 5 -iE "2002.*2001|403|forbidden"
```

### Get all 403 errors from today:
```bash
grep -i "403\|forbidden" /var/log/freeswitch/freeswitch.log | tail -20
```

### Get ACL deny messages:
```bash
grep -i "deny\|acl" /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001" | tail -20
```

### Get full call flow for debugging:
```bash
fs_cli -x "sofia loglevel all 9" && tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001"
```

## 🔍 Alternative: Check FreeSWITCH Console Directly

```bash
# Connect to FreeSWITCH console
fs_cli

# Enable verbose logging
sofia loglevel all 9
console loglevel debug

# Watch console output directly
# Then make the call and watch the output in real-time
```

## 📝 After Getting Logs

Once you have the logs, share them and look for:

1. **ACL deny messages** - Shows which ACL is blocking
2. **Authentication failures** - Shows auth issues
3. **Context/permission errors** - Shows dialplan issues
4. **Domain mismatch errors** - Shows domain format issues

**Common log patterns that cause 403:**
- `Denied by acl "..."` - ACL blocking
- `403 Forbidden` - Explicit rejection
- `Authentication failed` - Auth issue
- `Permission denied` - Extension permissions
- `Invalid domain` - Domain format issue

## 🎯 Recommended Command

**Run this before making the call:**
```bash
fs_cli -x "sofia loglevel all 9" && fs_cli -x "console loglevel debug" && tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden|deny|acl|reject|auth"
```

Then make the call from 2002 to 2001 and watch the output!
