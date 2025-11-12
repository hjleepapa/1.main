# Voice PIN Deployment Fix Guide

## 🚨 Issue

```
psycopg2.errors.UndefinedColumn: column users_convonet.voice_pin does not exist
```

The production database doesn't have the `voice_pin` column yet.

---

## ✅ Automatic Fix (Recommended)

### **The migration will run automatically on next deployment!**

When you push to Render.com, the build process will:
1. Run `build.sh`
2. Execute `deploy_setup.py`
3. Run `add_voice_pin.py` migration
4. Add the `voice_pin` column
5. Set admin PIN to '1234'

**Just wait for the next deployment to complete!** 🎉

---

## 🔧 Manual Fix (If Needed)

If you need to run the migration manually on Render.com:

### **Option 1: Run via Render Shell**

1. Go to Render.com dashboard
2. Open your web service
3. Click "Shell" tab
4. Run:
   ```bash
   python run_voice_pin_migration.py
   ```

### **Option 2: Run check_admin_user.py**

This script now auto-detects and fixes the missing column:

```bash
python check_admin_user.py
```

It will:
- ✅ Detect missing `voice_pin` column
- ✅ Add the column automatically
- ✅ Create index
- ✅ Set admin PIN to '1234'
- ✅ Verify admin user credentials

---

## 📊 What the Migration Does

### **SQL Commands:**

```sql
-- Add voice_pin column
ALTER TABLE users_convonet 
ADD COLUMN voice_pin VARCHAR(10) UNIQUE;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_users_voice_pin 
ON users_convonet(voice_pin);

-- Set admin user's PIN
UPDATE users_convonet 
SET voice_pin = '1234' 
WHERE email = 'admin@convonet.com';
```

---

## 🧪 Verify It Worked

### **Check 1: Database Column Exists**

Run this SQL query:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users_convonet' 
AND column_name = 'voice_pin';
```

Expected result:
```
column_name | data_type
------------|----------
voice_pin   | character varying
```

### **Check 2: Admin User Has PIN**

```sql
SELECT email, voice_pin 
FROM users_convonet 
WHERE email = 'admin@convonet.com';
```

Expected result:
```
email                    | voice_pin
------------------------|----------
admin@convonet.com     | 1234
```

### **Check 3: Web Login Works**

1. Go to https://hjlees.com/team-dashboard
2. Login with:
   - Email: `admin@convonet.com`
   - Password: `admin123`
3. Should login successfully ✅

### **Check 4: Voice PIN Works**

1. Call your Twilio number
2. Say: "one two three four"
   OR Press: 1234#
3. Should hear: "Welcome back, Admin!" ✅

---

## 📁 Migration Files

### **Created:**
- ✅ `convonet/migrations/add_voice_pin.py` - Main migration
- ✅ `run_voice_pin_migration.py` - Standalone runner
- ✅ `check_admin_user.py` - Updated with auto-column-add

### **Updated:**
- ✅ `deploy_setup.py` - Now runs voice_pin migration
- ✅ `build.sh` - Already configured (no changes needed)

---

## 🚀 Next Steps

### **After Deployment:**

1. **Wait for deployment to complete** on Render.com
2. **Check logs** for migration success:
   ```
   ✅ Voice PIN authentication migration completed successfully
   ✅ voice_pin column added
   ✅ Index created
   ✅ Admin user PIN set to '1234'
   ```
3. **Test voice authentication:**
   - Call Twilio number
   - Say "one two three four"
   - Should authenticate successfully
4. **Test web dashboard:**
   - Login with admin@convonet.com / admin123
   - Should work

---

## 🐛 Troubleshooting

### **Issue: Migration fails with "column already exists"**

**This is OK!** The migration checks for existing columns and skips gracefully.

### **Issue: Still getting "voice_pin does not exist"**

**Fix:**
```bash
# SSH into Render.com shell
python check_admin_user.py
```

This will force-add the column.

### **Issue: Admin user can't login**

**Fix:**
```bash
python check_admin_user.py
```

This will:
- Add voice_pin column if missing
- Reset admin password to 'admin123'
- Set voice PIN to '1234'

---

## ✅ Success Indicators

You'll know it worked when:

1. ✅ Deployment logs show: "Voice PIN authentication migration completed"
2. ✅ Web dashboard login works with admin@convonet.com / admin123
3. ✅ Voice call accepts PIN "one two three four" (or 1234#)
4. ✅ Agent says "Welcome back, Admin!"
5. ✅ No more database errors in logs

---

## 📞 Demo Credentials (After Fix)

**Web Login:**
- URL: https://hjlees.com/team-dashboard
- Email: admin@convonet.com
- Password: admin123

**Voice Authentication:**
- Call: Your Twilio number
- PIN (Speech): "one two three four"
- PIN (Keypad): 1234#

---

## 🎯 Summary

The `voice_pin` column is missing from production. This fix:

1. ✅ Adds migration to `deploy_setup.py`
2. ✅ Migration runs automatically on next deployment
3. ✅ Can also run manually if needed
4. ✅ `check_admin_user.py` is now self-healing
5. ✅ Safe: checks if column exists first

**Action Required:** Just push the code and wait for deployment! 🚀

