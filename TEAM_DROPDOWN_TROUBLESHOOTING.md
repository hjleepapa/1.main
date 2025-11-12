# Team Dropdown Troubleshooting Guide

## Problem: Team Dropdown is Empty

**Issue**: When logging into the team dashboard, the team dropdown shows no teams even though teams exist in the database.

## 🔍 **Diagnosis Steps**

### 1. Check Browser Console
1. **Login** to `https://hjlees.com/team-dashboard`
2. **Open Developer Tools** (F12)
3. **Check Console Tab** for debug messages:
   - `🔍 Loading user teams...`
   - `🔑 Access token: Present/Missing`
   - `📡 Response status: 200/401/500`
   - `📋 Teams data: {...}`
   - `⚠️ No teams found for user`

### 2. Common Issues & Solutions

#### **Issue A: Authentication Problem**
**Symptoms**: 
- `🔑 Access token: Missing`
- `📡 Response status: 401`

**Solution**:
1. **Clear browser cookies/cache**
2. **Re-login** with admin credentials:
   - Email: `admin@convonet.com`
   - Password: `admin123`

#### **Issue B: User Not Member of Teams**
**Symptoms**:
- `📡 Response status: 200`
- `📋 Teams data: {"teams": []}`
- `⚠️ No teams found for user`

**Solution**: Run the team membership fix script
```bash
# On production server
python fix_team_memberships.py
```

#### **Issue C: API Endpoint Error**
**Symptoms**:
- `📡 Response status: 500`
- Console shows server error

**Solution**: Check server logs for database connection issues

## 🛠️ **Quick Fix Commands**

### **Fix Team Memberships (Production)**
```bash
# SSH into production server
ssh user@hjlees.com

# Navigate to project directory
cd /path/to/project

# Run the fix script
python fix_team_memberships.py
```

### **Create Demo Team (If No Teams Exist)**
```bash
# Run the demo setup script
python create_users.py
```

## 🔧 **Manual Database Fix**

If the script doesn't work, manually fix the database:

```sql
-- 1. Check existing data
SELECT * FROM users_convonet WHERE email = 'admin@convonet.com';
SELECT * FROM teams_convonet;
SELECT * FROM team_memberships_convonet;

-- 2. Add admin to all teams
INSERT INTO team_memberships_convonet (team_id, user_id, role, joined_at)
SELECT t.id, u.id, 'owner', NOW()
FROM teams_convonet t
CROSS JOIN users_convonet u
WHERE u.email = 'admin@convonet.com'
AND NOT EXISTS (
    SELECT 1 FROM team_memberships_convonet tm
    WHERE tm.team_id = t.id AND tm.user_id = u.id
);
```

## 🎯 **Expected Behavior After Fix**

1. **Login** with admin credentials
2. **Team dropdown** should show:
   - `Demo Team (owner)`
   - Any other teams (owner)
3. **Auto-select** first team
4. **Load todos** for selected team
5. **Console logs** show:
   - `✅ Auto-selected team: Demo Team`
   - `👥 Adding team: Demo Team Role: owner`

## 🚨 **Emergency Fallback**

If nothing works, create a new team via API:

```bash
# Login and get token
curl -X POST https://hjlees.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@convonet.com", "password": "admin123"}'

# Create team (replace YOUR_TOKEN)
curl -X POST https://hjlees.com/api/teams/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Emergency Team", "description": "Created via API"}'
```

## 📋 **Debug Checklist**

- [ ] **Authentication**: User logged in successfully
- [ ] **Token**: Access token present in localStorage
- [ ] **API**: `/api/teams/` endpoint returns 200
- [ ] **Database**: Teams exist in `teams_convonet` table
- [ ] **Memberships**: User has memberships in `team_memberships_convonet`
- [ ] **JavaScript**: Console shows debug messages
- [ ] **UI**: Team dropdown populated with teams

## 🎉 **Success Indicators**

✅ **Team dropdown populated**  
✅ **Console shows**: `✅ Auto-selected team: [Team Name]`  
✅ **Todos load** for selected team  
✅ **Add Member button** works  
✅ **Create Todo** works with team context  

## 📞 **Still Having Issues?**

1. **Check server logs** for database errors
2. **Verify migration** ran successfully
3. **Test API endpoints** directly with curl
4. **Clear all browser data** and try again
5. **Check database connectivity** from server

---

**Most Common Fix**: Run `python fix_team_memberships.py` on the production server to add the admin user to existing teams.
