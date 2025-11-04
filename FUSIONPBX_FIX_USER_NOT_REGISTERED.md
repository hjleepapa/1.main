# Fix USER_NOT_REGISTERED Error - Extension 2002

## 🔍 Problem Identified

**Error:** `Cannot create outgoing channel of type [user] cause: [USER_NOT_REGISTERED]`

**Root Cause:** Extension 2002 exists in the database but is **not registered** with FreeSWITCH.

**Evidence:**
- ✅ Extension 2002 exists in database: `enabled = true`, `user_context = default`
- ❌ Extension 2002 NOT registered: `sofia status profile internal reg` shows nothing for 2002

## 🎯 Solution: Register Extension 2002

### Step 1: Verify Current Registration Status

```bash
# Check all registered extensions
fs_cli -x "sofia status profile internal reg"

# Check specifically for extension 2002 (should show nothing)
fs_cli -x "sofia status profile internal reg" | grep "2002"
```

### Step 2: Check Extension 2002 Configuration

```bash
# Verify extension exists and is enabled
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context, password, auth_acl FROM v_extensions WHERE extension = '2002';"
```

### Step 3: Check SIP Profile Settings

Make sure the `internal` SIP profile is running and configured correctly:

```bash
# Check if internal profile is running
fs_cli -x "sofia status"

# Check internal profile details
fs_cli -x "sofia status profile internal"
```

### Step 4: Configure SIP Phone for Extension 2002

Your SIP phone/softphone needs to register with FusionPBX. Use these settings:

#### SIP Account Settings:
- **SIP Server / Proxy:** `136.115.41.45` (or your FusionPBX IP)
- **SIP Port:** `5060` (default)
- **Username / Extension:** `2002`
- **Password:** (Check in FusionPBX GUI or database)
- **Domain / Realm:** `136.115.41.45`
- **Transport:** `UDP` (or `TCP` if configured)
- **Register:** `Yes` / `Enabled`

#### Get Extension 2002 Password:

**Option A: FusionPBX GUI**
1. Log into FusionPBX web interface
2. Go to **Accounts** → **Extensions**
3. Find extension **2002**
4. Check the **Password** field

**Option B: Database Query**
```bash
sudo -u postgres psql fusionpbx -c "SELECT extension, password FROM v_extensions WHERE extension = '2002';"
```

**Option C: Check Extension Details**
```bash
sudo -u postgres psql fusionpbx -c "SELECT extension, password, auth_acl, effective_caller_id_name, effective_caller_id_number FROM v_extensions WHERE extension = '2002';"
```

### Step 5: Verify Registration

After configuring the SIP phone, wait a few seconds and check:

```bash
# Check if extension 2002 is now registered
fs_cli -x "sofia status profile internal reg" | grep -A 5 "2002"

# Should show something like:
# reg_user=2002@136.115.41.45
# Contact: <sip:2002@192.168.x.x:5060>
```

### Step 6: Test the Call Again

Once extension 2002 is registered, try calling from extension 2001 again.

## 🔍 Troubleshooting Registration Issues

### Issue 1: SIP Phone Not Registering

**Check 1: Firewall Rules**
```bash
# Make sure UDP port 5060 is open
sudo ufw status | grep 5060

# If not, open it
sudo ufw allow 5060/udp
```

**Check 2: ACL Settings**
```bash
# Check if internal profile has proper ACL
fs_cli -x "sofia status profile internal" | grep -i acl

# Check ACL in database
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_access_control_nodes WHERE node_type = 'allow' AND node_cidr LIKE '%192.168%' OR node_cidr LIKE '%10.%';"
```

**Check 3: Registration Logs**
```bash
# Watch registration attempts in real-time
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "register|2002|auth"
```

### Issue 2: Wrong Password

If the password is incorrect, you'll see authentication errors:

```bash
# Check for auth failures
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "401|403|unauthorized|2002"
```

**Fix:** Update the password in FusionPBX GUI or reset it.

### Issue 3: Wrong Domain/Context

Make sure extension 2002 is using the correct domain:

```bash
# Check extension domain and context
sudo -u postgres psql fusionpbx -c "SELECT extension, domain_name, user_context FROM v_extensions WHERE extension = '2002';"

# Should match your SIP profile domain
fs_cli -x "sofia status profile internal" | grep "Domain"
```

### Issue 4: SIP Profile Not Accepting Registrations

Check if the internal profile has `apply-register-acl` set correctly:

```bash
# Check internal profile ACL settings
fs_cli -x "sofia xmlstatus profile internal" | grep -i "apply.*acl"
```

In FusionPBX:
1. Go to **Advanced** → **SIP Profiles**
2. Click on **internal**
3. Check **Apply Register ACL** - should be set to allow your network
4. Check **Apply Inbound ACL** - should allow registrations

## 📋 Quick Registration Test

Test if extension 2002 can register by manually checking registration:

```bash
# Force a registration check
fs_cli -x "sofia status profile internal reg 2002@136.115.41.45"

# Check all registrations
fs_cli -x "sofia status profile internal reg"
```

## 🎯 Expected Result

After extension 2002 registers successfully:

1. **Registration Check:**
   ```bash
   fs_cli -x "sofia status profile internal reg" | grep "2002"
   ```
   Should show:
   ```
   reg_user=2002@136.115.41.45
   ```

2. **Call Test:**
   - Call from extension 2001 to 2002 should work
   - No more `USER_NOT_REGISTERED` errors

## 🔧 Common SIP Phone Configuration Examples

### Grandstream Phones:
- **Account:** 2002
- **SIP Server:** 136.115.41.45
- **SIP User ID:** 2002
- **Authenticate ID:** 2002
- **Authenticate Password:** [password from FusionPBX]
- **Name:** Extension 2002

### Softphones (X-Lite, Zoiper, etc.):
- **Display Name:** 2002
- **User Name:** 2002
- **Password:** [password from FusionPBX]
- **Domain:** 136.115.41.45
- **Server / Proxy:** 136.115.41.45

### WebRTC Clients:
- **SIP URI:** `2002@136.115.41.45`
- **Password:** [password from FusionPBX]
- **Server:** `wss://136.115.41.45:7443` (for secure WebSocket)

## ✅ Verification Checklist

- [ ] Extension 2002 exists in database and is enabled
- [ ] Extension 2002 password is correct
- [ ] SIP phone is configured with correct settings
- [ ] SIP phone shows "Registered" status
- [ ] `fs_cli -x "sofia status profile internal reg"` shows 2002
- [ ] Firewall allows UDP port 5060
- [ ] Internal SIP profile ACL allows registration
- [ ] Call from 2001 to 2002 works without errors

## 🎯 Next Steps

1. **Configure SIP phone** for extension 2002 with correct credentials
2. **Verify registration** using `fs_cli` command
3. **Test call** from extension 2001 to 2002
4. If still not working, check the troubleshooting section above
