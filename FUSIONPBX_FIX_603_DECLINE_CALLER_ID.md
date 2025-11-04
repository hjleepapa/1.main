# Fix SIP 603 Decline - Extension 2003 Rejecting Calls

## 🔍 Problem Identified

**Error:** `SIP 603 Decline` / `CALL_REJECTED` when extension 2003 answers

**Evidence from logs:**
```
[DEBUG] sofia.c:7493 Channel sofia/internal/2003@198.27.217.12:61342 entering state [terminated][603]
[NOTICE] sofia.c:8736 Hangup sofia/internal/2003@198.27.217.12:61342 [CS_CONSUME_MEDIA] [CALL_REJECTED]
[DEBUG] mod_sofia.c:463 sofia/internal/2001@136.115.41.45 Overriding SIP cause 480 with 603 from the other leg
```

**Root Cause:** Extension 2003's phone is explicitly rejecting the call with SIP 603. Most likely causes:
1. **Caller ID is the extension itself** (e.g., 2001 calling shows as "2001" as caller ID)
2. **Phone has auto-reject enabled** for certain caller IDs
3. **Phone settings** configured to reject calls

## 🎯 Solution 1: Fix Caller ID in FusionPBX Dialplan

The FusionPBX dialplan might be setting the caller ID to the extension number, which phones often reject. We need to set proper caller ID.

### Check Current Caller ID Settings

```bash
# Check what caller ID is being sent
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "caller.*id|effective.*caller|origination.*caller" | grep -iE "2001|2003"
```

### Fix Caller ID via Database

Check and update extension 2001's caller ID:

```bash
# Check current caller ID settings for extension 2001
sudo -u postgres psql fusionpbx -c "SELECT extension, effective_caller_id_name, effective_caller_id_number, outbound_caller_id_name, outbound_caller_id_number FROM v_extensions WHERE extension = '2001';"

# Check extension 2003 settings too
sudo -u postgres psql fusionpbx -c "SELECT extension, effective_caller_id_name, effective_caller_id_number, outbound_caller_id_name, outbound_caller_id_number FROM v_extensions WHERE extension = '2003';"
```

### Fix via FusionPBX GUI

1. **Log into FusionPBX web interface**
2. Go to **Accounts** → **Extensions**
3. Click on extension **2001** (the one making the call)
4. Find **Caller ID** section
5. Set:
   - **Effective Caller ID Name:** Something descriptive like "Extension 2001" or "Agent 2001"
   - **Effective Caller ID Number:** `2001` (can keep as extension, or set to a display number)
   - **Outbound Caller ID Name:** Same as above
   - **Outbound Caller ID Number:** `2001` or a display number
6. **Save**
7. **Reload FreeSWITCH:**
   ```bash
   fs_cli -x "reload mod_sofia"
   fs_cli -x "reloadxml"
   ```

### Fix via SQL (If needed)

```bash
# Update extension 2001's caller ID
sudo -u postgres psql fusionpbx << EOF
UPDATE v_extensions 
SET 
  effective_caller_id_name = 'Extension 2001',
  outbound_caller_id_name = 'Extension 2001'
WHERE extension = '2001';
EOF

# Reload FreeSWITCH
fs_cli -x "reload mod_sofia"
fs_cli -x "reloadxml"
```

## 🎯 Solution 2: Check Phone Settings for Extension 2003

The phone itself might have settings causing it to reject calls.

### Common Phone Settings to Check:

1. **Call Rejection / Blacklist:**
   - Check if extension 2001 is in a blacklist
   - Disable auto-reject features

2. **Call Filtering:**
   - Check if the phone has call filtering enabled
   - Verify it's not set to reject calls from specific numbers

3. **Do Not Disturb (DND):**
   - Make sure DND is disabled on extension 2003's phone

4. **Call Settings:**
   - Check if "Reject anonymous calls" is enabled (might reject if caller ID is missing)
   - Check if "Reject calls from blocked numbers" is enabled

### Test from FusionPBX CLI:

Test if FreeSWITCH can successfully call extension 2003:

```bash
# Test calling extension 2003 directly from FreeSWITCH CLI
fs_cli -x "originate {origination_caller_id_name='Test Call',origination_caller_id_number='9999'}user/2003@136.115.41.45 &echo()"
```

**If this works:** The issue is with the caller ID from extension 2001
**If this also fails:** The issue is with extension 2003's phone settings or configuration

## 🎯 Solution 3: Check Dialplan Caller ID Export

Check if the dialplan is properly exporting caller ID:

```bash
# Check dialplan for caller ID exports
grep -r "caller.*id" /usr/share/freeswitch/conf/dialplan/default/
grep -r "effective.*caller" /usr/share/freeswitch/conf/dialplan/default/
```

Or check in FusionPBX:
1. Go to **Advanced** → **Dialplans**
2. Find the dialplan for `136.115.41.45` domain
3. Look for **Actions** that set caller ID

## 🎯 Solution 4: Force Caller ID in Dialplan Action

If needed, we can force caller ID in the dialplan action. Check what action is being used for extension-to-extension calls:

```bash
# Find the dialplan context and action
grep -A 10 "bridge(user/" /usr/share/freeswitch/conf/dialplan/default/*.xml
```

In FusionPBX dialplan, modify the bridge action to include caller ID:

**Original:**
```xml
<action application="bridge" data="user/${destination_number}@${domain_name}"/>
```

**Modified (if needed):**
```xml
<action application="set" data="effective_caller_id_name=Extension ${caller_id_number}"/>
<action application="set" data="effective_caller_id_number=${caller_id_number}"/>
<action application="bridge" data="user/${destination_number}@${domain_name}"/>
```

**Note:** Be careful modifying dialplans directly - FusionPBX generates them. It's better to fix via GUI or database.

## 🔍 Diagnostic Commands

### Check What Caller ID Is Being Sent

```bash
# Enable detailed logging and make a call
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Then make the call and check logs for caller ID
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "caller|From:|effective.*caller" | grep -iE "2001|2003"
```

### Check SIP INVITE Message

Look for the SIP INVITE message sent to extension 2003:

```bash
# Get SIP INVITE details
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "INVITE|From:|To:" | grep -iE "2003" | tail -20
```

## 📋 Quick Fix Checklist

- [ ] Check extension 2001's caller ID settings in FusionPBX
- [ ] Set proper Caller ID Name (not just number)
- [ ] Check extension 2003's phone settings for auto-reject
- [ ] Disable any blacklist or call filtering on extension 2003's phone
- [ ] Test call with different caller ID from CLI
- [ ] Verify caller ID in SIP INVITE messages
- [ ] Reload FreeSWITCH after making changes

## 🎯 Most Likely Fix

Based on the logs, the most likely issue is that **extension 2001 is calling with its extension number as caller ID**, and extension 2003's phone is rejecting it (possibly because it thinks it's calling itself, or due to phone settings).

**Quick fix:**
1. Set extension 2001's **Effective Caller ID Name** to something descriptive like "Extension 2001" in FusionPBX GUI
2. Make sure it's not just the number
3. Reload FreeSWITCH
4. Test the call again

## ✅ Verification

After making changes:

1. **Reload FreeSWITCH:**
   ```bash
   fs_cli -x "reload mod_sofia"
   fs_cli -x "reloadxml"
   ```

2. **Make a test call** from 2001 to 2003

3. **Check logs** for caller ID:
   ```bash
   tail -100 /var/log/freeswitch/freeswitch.log | grep -iE "caller|2001.*2003|603|CALL_REJECTED"
   ```

4. **Expected result:** No more 603 Decline, call should connect successfully
