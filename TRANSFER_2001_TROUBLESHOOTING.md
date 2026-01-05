# Call Transfer to Extension 2001 - Troubleshooting Guide

## Problem
Call transfer to extension 2001 is failing with `WRONG_CALL_STATE` error in FusionPBX logs.

## Symptoms
- Twilio successfully queues the call to `sip:2001@136.115.41.45;transport=udp`
- FusionPBX receives the INVITE from Twilio
- Call is abandoned with error: `WRONG_CALL_STATE`
- Extension 2001 never rings

## Root Cause
FusionPBX receives the SIP call but cannot route it to extension 2001 because:
1. The dialplan context doesn't know how to route external SIP calls to extensions
2. Extension 2001 might not exist or be configured incorrectly
3. The SIP gateway/trunk routing is not configured

## Solution: Configure FusionPBX Dialplan for External SIP Routing

### Step 1: Verify Extension 2001 Exists

SSH into FusionPBX and check if extension 2001 exists:

```bash
sudo -u postgres psql fusionpbx -c "SELECT extension, user_context, enabled FROM v_extensions WHERE extension = '2001';"
```

**Expected output:**
```
 extension | user_context | enabled 
-----------+--------------+---------
 2001      | default      | true
```

If extension doesn't exist, create it first in FusionPBX web UI.

### Step 2: Check Current Dialplan Context

Check what context external SIP calls use:

```bash
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_dialplans WHERE dialplan_name LIKE '%public%' OR dialplan_name LIKE '%external%' OR dialplan_name LIKE '%from-twilio%';"
```

### Step 3: Create or Update Dialplan for External SIP Calls

The call from Twilio needs to be routed through a dialplan context. You have two options:

#### Option A: Create a "from-twilio" Context (Recommended)

1. **SSH into FusionPBX:**
   ```bash
   ssh root@136.115.41.45
   ```

2. **Check if dialplan exists:**
   ```bash
   sudo -u postgres psql fusionpbx -c "SELECT * FROM v_dialplans WHERE dialplan_name = 'from-twilio';"
   ```

3. **Create dialplan via SQL (if it doesn't exist):**
   ```bash
   sudo -u postgres psql fusionpbx <<EOF
   INSERT INTO v_dialplans (dialplan_uuid, domain_uuid, dialplan_name, dialplan_number, dialplan_context, dialplan_enabled, dialplan_description)
   SELECT gen_random_uuid(), domain_uuid, 'from-twilio', '^(.+)$', 'from-twilio', 'true', 'Route Twilio SIP calls to extensions'
   FROM v_domains LIMIT 1;
   
   INSERT INTO v_dialplan_details (dialplan_detail_uuid, domain_uuid, dialplan_uuid, dialplan_detail_tag, dialplan_detail_type, dialplan_detail_data, dialplan_detail_order)
   SELECT gen_random_uuid(), domain_uuid, dialplan_uuid, 'action', 'transfer', '\${EXTEN} XML default', 10
   FROM v_dialplans WHERE dialplan_name = 'from-twilio';
   EOF
   ```

4. **Reload dialplan:**
   ```bash
   fs_cli -x "reloadxml"
   ```

#### Option B: Use FusionPBX Web UI to Create Dialplan

1. **Login to FusionPBX:** https://136.115.41.45
2. **Navigate:** Advanced → Dialplans → Add
3. **Configure:**
   - **Name:** `from-twilio`
   - **Number:** `^(.+)$`
   - **Context:** `from-twilio`
   - **Enabled:** Yes
   - **Description:** Route Twilio SIP calls to extensions

4. **Add Dialplan Entry:**
   - **Tag:** `action`
   - **Type:** `transfer`
   - **Data:** `${EXTEN} XML default`
   - **Order:** `10`

5. **Save and Apply Configuration**

### Step 4: Configure SIP Gateway/Trunk for Twilio

The external SIP profile needs to route calls to the correct context.

1. **Check SIP Gateway settings:**
   ```bash
   sudo -u postgres psql fusionpbx -c "SELECT * FROM v_gateways WHERE gateway_name LIKE '%twilio%' OR gateway_name LIKE '%external%';"
   ```

2. **Check SIP Profile context:**
   ```bash
   fs_cli -x "sofia status profile external"
   ```

3. **In FusionPBX Web UI:**
   - Navigate: **Advanced → Gateways → Add**
   - **Gateway Name:** `Twilio-SIP`
   - **Proxy/Username:** (leave empty for IP-based auth)
   - **From Domain:** `136.115.41.45`
   - **Context:** `from-twilio` (or `public` if you use that)
   - **Enabled:** Yes

### Step 5: Verify SIP Profile Context

1. **Login to FusionPBX Web UI**
2. **Navigate:** Advanced → SIP Profiles → external
3. **Check Context Setting:**
   - Look for `context` setting
   - It should be set to `public` or `from-twilio`
   - If it's set to something else, change it to `public`

4. **Check apply-inbound-acl:**
   - Should be set to `Twilio-SIP` (you already configured this)
   - Enabled: Yes

### Step 6: Create/Verify Public Context Routes to Extensions

The `public` context should route calls to extensions:

1. **Check public dialplan:**
   ```bash
   sudo -u postgres psql fusionpbx -c "SELECT * FROM v_dialplans WHERE dialplan_context = 'public';"
   ```

2. **Check if public context routes to extensions:**
   ```bash
   fs_cli -x "dialplan show public"
   ```

   You should see something like:
   ```
   Context 'public' created by 'pbx_config'
   '2001' => 1. NoOp(Incoming call) [pbx_config]
            2. Transfer(2001 XML default) [pbx_config]
   ```

3. **If public context doesn't route to extensions, create it:**
   - Navigate: **Advanced → Dialplans → Add**
   - **Name:** `public-extension-routing`
   - **Number:** `^(\d{4})$` (matches 4-digit extensions)
   - **Context:** `public`
   - **Enabled:** Yes
   - **Dialplan Entry:**
     - Tag: `action`
     - Type: `transfer`
     - Data: `${EXTEN} XML default`
     - Order: 10

### Step 7: Test the Configuration

1. **Reload everything:**
   ```bash
   fs_cli -x "reloadxml"
   fs_cli -x "sofia profile external rescan"
   ```

2. **Monitor logs in real-time:**
   ```bash
   tail -f /var/log/freeswitch/freeswitch.log | grep -E "2001|WRONG_CALL_STATE"
   ```

3. **Test the transfer from your application**

4. **Expected log output (success):**
   ```
   [NOTICE] New Channel sofia/internal/+12344007818@sip.twilio.com
   [INFO] Executing [2001@public:1] NoOp
   [INFO] Executing [2001@public:2] Transfer
   [NOTICE] Extension 2001 ringing
   ```

### Step 8: Alternative - Use Gateway with Explicit Routing

If the above doesn't work, configure a SIP gateway explicitly:

1. **Create SIP Gateway in FusionPBX:**
   - **Advanced → Gateways → Add → SIP Gateway**
   - **Gateway Name:** `Twilio-External`
   - **Proxy:** (leave empty)
   - **From Domain:** `136.115.41.45`
   - **Context:** `public`
   - **Enabled:** Yes
   - **Advanced Settings:**
     - `proxy` → (leave empty)
     - `register` → `false`
     - `caller-id-in-from` → `false`

2. **Update your code to use gateway context:**
   The SIP URI format might need to include the context:
   ```python
   sip_uri = f"sip:2001@136.115.41.45;transport=udp;context=public"
   ```

### Quick Diagnostic Commands

```bash
# Check if extension exists
sudo -u postgres psql fusionpbx -c "SELECT extension, user_context, enabled FROM v_extensions WHERE extension = '2001';"

# Check dialplan contexts
fs_cli -x "dialplan show public"
fs_cli -x "dialplan show from-twilio"

# Check SIP profile context
fs_cli -x "sofia status profile external"

# Monitor calls in real-time
fs_cli -x "console loglevel debug"
tail -f /var/log/freeswitch/freeswitch.log
```

## Most Likely Fix

Based on the error, the most likely issue is that the `public` context doesn't have a dialplan entry to route 4-digit numbers to extensions. 

**Quick fix:** Create a dialplan in the `public` context that matches `^(\d{4})$` and transfers to `${EXTEN} XML default`.

