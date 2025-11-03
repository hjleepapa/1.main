# FusionPBX Quick Setup for Twilio Transfer

## The One Thing You're Missing

Based on your error logs and screenshots, you have:
- ✅ Access Control List `Twilio-SIP` created correctly
- ❌ **SIP Profile not configured to USE the ACL**

## Quick Fix

### Via FusionPBX GUI (Easiest)

1. Login: `https://136.115.41.45`
2. Go to: `Advanced → SIP Profiles → external`
3. Find the row labeled: `apply-inbound-acl`
4. Change its **Value** to: `Twilio-SIP`
5. Make sure **Enabled** is checked ✅
6. Click **Save** at the bottom
7. Go to: `Status → SIP Status`
8. Find "external" profile
9. Click **Reload XML**
10. Click **Restart**

That's it! The SIP profile now knows to use your `Twilio-SIP` ACL.

### Via Database (If GUI Doesn't Work)

```bash
ssh root@136.115.41.45

# PostgreSQL
sudo -u postgres psql fusionpbx

UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'Twilio-SIP'
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

UPDATE v_sip_profile_settings sps
SET sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

\q

fs_cli -x "reload"
```

---

## What's Happening?

1. You created the **Access Control List** → ✅ Twilio IPs are whitelisted
2. But the **SIP Profile** doesn't know to **apply** that ACL → ❌ Still rejecting calls
3. You need to tell the SIP profile: "Use the Twilio-SIP ACL" → Missing step!

**Think of it like this:**
- ACL = A list of allowed guests
- SIP Profile = The bouncer at the door
- You created the guest list ✅
- But forgot to tell the bouncer to check it ❌

---

## Verify It Worked

```bash
ssh root@136.115.41.45
fs_cli -x "sofia xmlstatus profile external" | grep -i "apply-inbound-acl"
```

Should show:
```
<apply-inbound-acl>Twilio-SIP</apply-inbound-acl>
```

---

## Then Test

Make a test transfer call. Watch logs:

```bash
ssh root@136.115.41.45
fs_cli -x "console loglevel 9"
```

You should see SIP INVITE from Twilio IP being accepted, not rejected.

