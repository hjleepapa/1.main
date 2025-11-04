# Analyze 403 Forbidden Logs - Extension-to-Extension Calling

## 🔍 What the Logs Show

Your logs show:
1. ✅ Extension 2001 is making the call
2. ✅ Dialplan is processing the call to extension 2002
3. ✅ Bridge command is executed: `bridge(user/2002@136.115.41.45)`
4. ❌ **No logs showing what happens when trying to reach extension 2002**

The logs stop at the bridge command, which means we need to see what happens when FreeSWITCH tries to actually contact extension 2002.

## 🔎 Get More Specific Logs

### Check 1: Look for SIP INVITE to Extension 2002

```bash
# Get logs showing SIP INVITE messages to extension 2002
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "2002|sofia.*2002|invite.*2002" | tail -30
```

### Check 2: Look for Channel Creation for Extension 2002

```bash
# Look for new channel creation for extension 2002
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "New Channel.*2002|sofia.*2002" | tail -30
```

### Check 3: Check if Extension 2002 is Registered

```bash
# Check if extension 2002 is registered
fs_cli -x "sofia status profile internal reg" | grep "2002"

# Should show registration details if it's registered
```

### Check 4: Get Full Call Flow with Timestamps

```bash
# Get logs around the call time (adjust timestamp as needed)
grep -iE "536ad1aa-f360-42b1-b3bd-5e843842d965|2002" /var/log/freeswitch/freeswitch.log | tail -50
```

### Check 5: Look for 403 Response Codes

```bash
# Search for 403 SIP response codes
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "403|SIP/2.0 403|Forbidden"
```

### Check 6: Check ACL/Authentication Messages

```bash
# Look for ACL or auth errors
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "denied|acl|auth.*2002|permission.*2002"
```

## 🎯 Key Questions to Answer

Run these commands to get the missing information:

### 1. Is Extension 2002 Registered?

```bash
fs_cli -x "sofia status profile internal reg" | grep -A 5 "2002"
```

**Expected:** Should show extension 2002 registered
**If not:** Extension 2002 needs to register

### 2. Does Extension 2002 Exist?

```bash
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context FROM v_extensions WHERE extension = '2002';"
```

### 3. What Happens When Bridge Tries to Contact Extension 2002?

```bash
# Get logs after the bridge command
grep -A 20 "bridge(user/2002@136.115.41.45)" /var/log/freeswitch/freeswitch.log | tail -30
```

### 4. Check for SIP Response Codes

```bash
# Look for SIP response codes (403, 404, 486, etc.)
tail -500 /var/log/freeswitch/freeswitch.log | grep -E "SIP/2.0 [4-6][0-9][0-9]|^[0-9]{3} " | tail -20
```

## 🔍 What to Look For

Based on your logs, the bridge command is executed but we need to see:

1. **SIP INVITE to extension 2002** - Is FreeSWITCH sending the INVITE?
2. **SIP Response from extension 2002** - What response comes back?
3. **Channel creation** - Does a channel get created for extension 2002?
4. **ACL check** - Is an ACL blocking the call?
5. **Registration status** - Is extension 2002 actually registered?

## 🎯 Recommended Next Steps

### Step 1: Enable Maximum Logging and Try Again

```bash
# Enable maximum logging
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Clear previous logs (optional)
# tail -0 /var/log/freeswitch/freeswitch.log > /dev/null

# Watch logs in real-time with more context
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|403|forbidden|deny|acl|invite|bridge.*2002"
```

Then make the call again from 2001 to 2002.

### Step 2: Check Extension 2002 Status

```bash
# Check if extension 2002 exists and is enabled
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context, do_not_disturb FROM v_extensions WHERE extension = '2002';"

# Check if extension 2002 is registered
fs_cli -x "sofia status profile internal reg" | grep -A 10 "2002"
```

### Step 3: Try Originating from CLI

Test if FreeSWITCH can call extension 2002 directly:

```bash
# Test calling extension 2002 from FreeSWITCH CLI
fs_cli -x "originate user/2002@136.115.41.45 &echo()"
```

**If this works:** The issue is with how the SIP client (2001) is making the call
**If this fails:** The issue is with extension 2002 configuration or registration

## 📋 Complete Diagnostic Script

Run this to get all relevant information:

```bash
#!/bin/bash
echo "=== Extension 2002 Diagnostic ==="
echo ""

echo "1. Extension 2002 Database Check:"
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context, do_not_disturb FROM v_extensions WHERE extension = '2002';"
echo ""

echo "2. Extension 2002 Registration Status:"
fs_cli -x "sofia status profile internal reg" | grep -A 10 "2002"
echo ""

echo "3. Recent Logs with Extension 2002:"
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "2002" | tail -20
echo ""

echo "4. Recent 403/Forbidden Errors:"
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "403|forbidden" | tail -10
echo ""

echo "5. Recent Bridge Attempts to 2002:"
grep -i "bridge.*2002" /var/log/freeswitch/freeswitch.log | tail -5
echo ""

echo "6. Test Originate from CLI:"
echo "   (This will attempt to call extension 2002)"
fs_cli -x "originate user/2002@136.115.41.45 &echo()"
```

## 🔍 Most Likely Issues Based on Missing Logs

Since we don't see any SIP INVITE messages to extension 2002 in your logs, the issue is likely:

1. **Extension 2002 not registered** - FreeSWITCH can't reach it
2. **Extension 2002 doesn't exist** - Not configured in FusionPBX
3. **Extension 2002 disabled** - Disabled in FusionPBX
4. **SIP client issue** - The SIP client isn't properly sending the call

## 🎯 Immediate Actions

**Run these commands and share the output:**

```bash
# 1. Check if extension 2002 is registered
fs_cli -x "sofia status profile internal reg" | grep "2002"

# 2. Check if extension 2002 exists
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled FROM v_extensions WHERE extension = '2002';"

# 3. Get logs showing what happens after bridge command
grep -A 30 "bridge(user/2002@136.115.41.45)" /var/log/freeswitch/freeswitch.log | tail -40
```

These will help identify why the bridge to extension 2002 is failing!
