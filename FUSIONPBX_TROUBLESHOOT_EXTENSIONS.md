# FusionPBX Extension Troubleshooting Guide

## Your Current Situation

✅ **Extension 2001 IS registered** (shows Contact: `sip:2001@198.27.217.12:55965`)  
❌ **But `user_exists` returns false** - likely a domain mismatch issue

## Correct Commands for Your Setup

### Check Extension Registration (CORRECT)

```bash
# Check ALL registered extensions on internal profile
fs_cli -x "sofia status profile internal reg"

# Check specific extension registration
fs_cli -x "sofia status profile internal reg" | grep -i "2001\|2002"

# Your extension is registered to domain: 136.115.41.45 (your IP)
# So check with that domain:
fs_cli -x "user_exists id 2001 domain-name 136.115.41.45"
```

### Check Extension in Directory (Multiple Methods)

```bash
# Method 1: Check with IP as domain
fs_cli -x "user_exists id 2001 domain-name 136.115.41.45"

# Method 2: Check with 'default' domain (if configured)
fs_cli -x "user_exists id 2001 domain-name default"

# Method 3: Check all domains and find where 2001 exists
fs_cli -x "user_data 2001@136.115.41.45 var"

# Method 4: List all users in directory
fs_cli -x "xml_locate directory"
```

### Check Dialplan (CORRECT Syntax)

```bash
# FreeSWITCH doesn't use "dialplan_lookup context=..." syntax
# Instead, use these commands:

# Reload dialplan first
fs_cli -x "reloadxml"

# Check what dialplan contexts exist
fs_cli -x "xml_locate dialplan"

# Test dialing extension 2001 from external context
fs_cli -x "originate {origination_caller_id_number=Twilio,origination_caller_id_name=Twilio,context=public,domain_name=136.115.41.45}user/2001@136.115.41.45 &echo"

# Or simpler test
fs_cli -x "originate user/2001@136.115.41.45 &echo"
```

### Find CDR Logs (Correct Locations)

```bash
# CDR location might be different - check these:
ls -la /var/log/freeswitch/cdr-csv/
ls -la /var/log/freeswitch/cdr-csv/*.csv

# Or check FusionPBX database for CDR
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_xml_cdr ORDER BY start_stamp DESC LIMIT 10;"

# Or via FusionPBX GUI:
# Reports → CDR → Search (filter by extension 2001)
```

### Check Extension Details from Database

```bash
# Check if extension exists in FusionPBX database
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, description FROM v_extensions WHERE extension IN ('2001', '2002');"

# Check extension user details
sudo -u postgres psql fusionpbx -c "SELECT extension, user_uuid, domain_uuid FROM v_extensions WHERE extension IN ('2001', '2002');"

# Check what domain the extensions belong to
sudo -u postgres psql fusionpbx -c "SELECT e.extension, d.domain_name FROM v_extensions e JOIN v_domains d ON e.domain_uuid = d.domain_uuid WHERE e.extension IN ('2001', '2002');"
```

### Check Extension Registration Details

```bash
# Get detailed registration info for 2001
fs_cli -x "sofia status profile internal reg" | grep -A 10 "2001"

# Check user data
fs_cli -x "user_data 2001@136.115.41.45 var presence_id"
fs_cli -x "user_data 2001@136.115.41.45 var contact"

# Check if extension can receive calls
fs_cli -x "user_callcenter 2001@136.115.41.45 status"
```

## Why Dialing Might Fail

### 1. Domain Mismatch

Your extension is registered as `2001@136.115.41.45`, but your transfer code might be using:
- `sip:2001@136.115.41.45` ✅ Correct
- `sip:2001@default` ❌ Wrong domain

**Check your transfer code:**
```bash
# Check what SIP URI your code is sending
grep -r "sip:2001" sambanova/
grep -r "2001@" sambanova/
```

### 2. Context Mismatch

Twilio calls come in on `external` profile, which uses context `public` or `from-external`.  
Extension 2001 might be in context `default` or `from-internal`.

**Check contexts:**
```bash
# Check what context external profile uses
fs_cli -x "sofia xmlstatus profile external" | grep context

# Check extension's context in database
sudo -u postgres psql fusionpbx -c "SELECT extension, user_context FROM v_extensions WHERE extension = '2001';"

# Check dialplan for external → extension routing
fs_cli -x "reloadxml"
fs_cli -x "xml_locate dialplan public"
```

### 3. Extension Not Reachable from External Profile

**Test if extension can be dialed from external context:**

```bash
# This simulates a call from external profile
fs_cli -x "originate {origination_caller_id_number=Twilio,context=public,domain_name=136.115.41.45}user/2001@136.115.41.45 &echo"
```

### 4. Check Main Log for Actual Errors

```bash
# Watch logs in real-time while attempting transfer
tail -f /var/log/freeswitch/freeswitch.log

# Or search for recent errors
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "2001|2002|error|fail|NOT_FOUND|USER_NOT_REGISTERED"
```

## Quick Diagnostic Script

Run this to check everything at once:

```bash
#!/bin/bash
echo "=== Extension 2001 Diagnostic ==="
echo ""
echo "1. Check registration:"
fs_cli -x "sofia status profile internal reg" | grep -i "2001"
echo ""
echo "2. Check database:"
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context, domain_uuid FROM v_extensions WHERE extension = '2001';"
echo ""
echo "3. Check domain:"
sudo -u postgres psql fusionpbx -c "SELECT e.extension, d.domain_name FROM v_extensions e JOIN v_domains d ON e.domain_uuid = d.domain_uuid WHERE e.extension = '2001';"
echo ""
echo "4. Check external profile context:"
fs_cli -x "sofia xmlstatus profile external" | grep -i context
echo ""
echo "5. Recent log errors:"
tail -50 /var/log/freeswitch/freeswitch.log | grep -iE "2001|error|NOT_FOUND" | tail -10
```

## Most Likely Issue

Based on your output, extension 2001 **IS registered** and working. The failure is likely:

1. **Wrong SIP URI format** in your transfer code
2. **Context routing issue** - external calls can't reach extension
3. **Domain mismatch** - using wrong domain in SIP URI

**Next Steps:**
1. Check what SIP URI your code sends: `grep -r "sip:2001" sambanova/`
2. Check extension's context: `sudo -u postgres psql fusionpbx -c "SELECT extension, user_context FROM v_extensions WHERE extension = '2001';"`
3. Check dialplan routing from `public` context to extension
