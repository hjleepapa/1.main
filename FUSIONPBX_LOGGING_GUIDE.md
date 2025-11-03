# FusionPBX/FreeSWITCH Logging Guide

## Finding Logs for Failed Dialing

### Main Log Locations

**FreeSWITCH Main Log:**
```bash
# Main log file
/var/log/freeswitch/freeswitch.log

# Rotated logs (daily)
/var/log/freeswitch/freeswitch.log.2024-01-15

# CDR (Call Detail Records) - shows all call attempts
/var/log/freeswitch/cdr-csv/Master.csv
```

### Quick Log Commands

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# View recent log entries (last 100 lines)
tail -100 /var/log/freeswitch/freeswitch.log

# Follow log in real-time (press Ctrl+C to stop)
tail -f /var/log/freeswitch/freeswitch.log

# Search for extension 2001 or 2002
grep -i "2001\|2002" /var/log/freeswitch/freeswitch.log | tail -50

# Search for errors related to extensions
grep -i "error\|fail\|reject" /var/log/freeswitch/freeswitch.log | grep -i "2001\|2002" | tail -50

# Check CDR for call attempts
tail -50 /var/log/freeswitch/cdr-csv/Master.csv | grep -i "2001\|2002"
```

### Enable Detailed Logging via fs_cli

```bash
# Connect to FreeSWITCH CLI
fs_cli

# Enable debug logging (level 9 = most verbose)
fs_cli> console loglevel 9

# Enable SIP debug logging
fs_cli> sofia loglevel all 9

# Enable dialplan debug
fs_cli> dialplan_loglevel 9

# Watch logs in real-time
fs_cli> /log level 9

# Exit fs_cli
fs_cli> /exit
```

### Check Specific Extension Issues

```bash
# Check if extension 2001 exists in directory
fs_cli -x "user_exists id 2001 domain-name default"

# Check extension details
fs_cli -x "xml_locate directory domain default 2001"

# Check dialplan for extension
fs_cli -x "dialplan_lookup context=public number=2001"

# Check what happens when dialing extension
fs_cli -x "originate user/2001@default &echo"
```

### Search for Twilio Transfer Failures

```bash
# Search for Twilio-related logs
grep -i "twilio\|136.115.41.45\|sip:2001" /var/log/freeswitch/freeswitch.log | tail -50

# Search for SIP INVITE failures
grep -i "invite\|487\|404\|408\|503" /var/log/freeswitch/freeswitch.log | grep -i "2001\|2002" | tail -50

# Search for authentication failures
grep -i "auth\|401\|403" /var/log/freeswitch/freeswitch.log | tail -50
```

### Check SIP Profile Logs

```bash
# Check external profile status
fs_cli -x "sofia status profile external"

# Check SIP traces (if enabled)
ls -la /var/log/freeswitch/sip-traces/

# Enable SIP trace capture
fs_cli -x "sofia global siptrace on"
```

### Common Error Messages to Look For

**Extension Not Found (404):**
```
NOT_FOUND [sofia_contact(2001@default)]
```
**Solution:** Extension doesn't exist or wrong domain

**User Not Registered:**
```
USER_NOT_REGISTERED [2001@default]
```
**Solution:** Extension exists but phone isn't registered

**Invalid Gateway:**
```
INVALID_GATEWAY
```
**Solution:** SIP profile configuration issue

**Call Rejected:**
```
CALL_REJECTED
```
**Solution:** ACL or firewall blocking

**Timeout:**
```
TIMEOUT
```
**Solution:** Network or routing issue

### Real-Time Monitoring During Transfer

```bash
# Terminal 1: Follow main log
tail -f /var/log/freeswitch/freeswitch.log

# Terminal 2: Follow SIP log
fs_cli -x "/log level 7"
fs_cli -x "sofia loglevel all 7"

# Terminal 3: Watch for calls
watch -n 1 'fs_cli -x "show channels"'
```

### Check Extension Registration Status

```bash
# Check if extension 2001 is registered
fs_cli -x "sofia status profile internal reg" | grep -i 2001

# Check all registrations
fs_cli -x "sofia status profile internal reg"

# Check if extension is active
fs_cli -x "user_data 2001@default var presence_id"
```

### Check Dialplan Context

```bash
# List all dialplan contexts
fs_cli -x "dialplan_reload"
fs_cli -x "xml_locate dialplan"

# Test dialplan for extension 2001
fs_cli -x "dialplan_lookup context=public number=2001"
fs_cli -x "dialplan_lookup context=from-external number=2001"
fs_cli -x "dialplan_lookup context=default number=2001"
```

### FusionPBX Web GUI Logs

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **View Logs:**
   - `Status → System Logs → FreeSWITCH Log`
   - `Status → SIP Status → Logs`
   - `Status → System Status → Log Viewer`

3. **CDR (Call Detail Records):**
   - `Reports → CDR → Search`
   - Filter by extension: `2001` or `2002`
   - Check call status and duration

### Enable Verbose Logging in FusionPBX GUI

1. **Go to:** `Advanced → System → Settings`
2. **Find:** `Log Level` or `Debug Level`
3. **Set to:** `DEBUG` or `9`
4. **Save**
5. **Reload FreeSWITCH:** `Status → SIP Status → Reload`

### Export Logs for Analysis

```bash
# Export last 1000 lines of log with errors
grep -i "error\|fail\|2001\|2002" /var/log/freeswitch/freeswitch.log | tail -1000 > /tmp/dialing_errors.log

# Export all SIP INVITE attempts
grep -i "invite.*2001\|invite.*2002" /var/log/freeswitch/freeswitch.log > /tmp/sip_invites.log

# Export CDR for last 24 hours
tail -100 /var/log/freeswitch/cdr-csv/Master.csv > /tmp/cdr_export.csv
```

### Most Useful Command for Your Issue

Run this single command to see recent failures:

```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# One command to rule them all
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "2001|2002|error|fail|invite" | tail -50
```

This will show the last 50 relevant log entries about extensions 2001/2002, errors, failures, and INVITE attempts.
