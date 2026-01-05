# Render.com Environment Variables Setup Guide

## Problem: Environment Variables Showing as "NOT SET"

If you're seeing logs like:
```
• GOOGLE_OAUTH2_TOKEN_B64: NOT SET
• GOOGLE_CLIENT_ID: NOT SET
```

Even though you've set them in Render.com, here's how to fix it.

## Step-by-Step: Setting Environment Variables in Render.com

### 1. Navigate to Your Service

1. Go to https://dashboard.render.com/
2. Click on your service (e.g., "convonet" or your service name)
3. Click on **Environment** in the left sidebar

### 2. Add Environment Variables

1. In the **Environment Variables** section, click **Add Environment Variable**
2. For each variable, add:

   **Variable Name:** `GOOGLE_OAUTH2_TOKEN_B64`  
   **Value:** (paste your base64 token - NO QUOTES)

   **Variable Name:** `GOOGLE_CLIENT_ID`  
   **Value:** (paste your client ID)

   **Variable Name:** `GOOGLE_CLIENT_SECRET`  
   **Value:** (paste your client secret)

### 3. Important: No Quotes!

❌ **WRONG:**
```
GOOGLE_OAUTH2_TOKEN_B64="gAAAAAB..."
```

✅ **CORRECT:**
```
GOOGLE_OAUTH2_TOKEN_B64=gAAAAAB...
```

### 4. Save Changes

After adding all variables:
1. Click **Save Changes** at the bottom
2. **Wait for the page to reload** (this ensures changes are saved)

### 5. **CRITICAL: Restart Your Service**

**This is the most common issue!** Environment variables are only loaded when the service starts.

1. Go to **Manual Deploy** in the left sidebar
2. Click **Clear build cache & deploy**
3. Wait for deployment to complete (usually 2-5 minutes)
4. Check the deployment logs to ensure it started successfully

## Verify Environment Variables Are Set

### Option 1: Use Debug Endpoint (After Deployment)

After deploying, visit:
- `https://your-domain.com/debug/env/google` - Check Google Calendar variables
- `https://your-domain.com/debug/env/all` - List all environment variables

### Option 2: Check in Render.com Dashboard

1. Go to **Environment** → **Environment Variables**
2. Verify all variables are listed (they should show as "● ● ● ● ●" for security)
3. Check the count matches what you added

### Option 3: Check Application Logs

After restarting, look for logs that show:
```
• GOOGLE_OAUTH2_TOKEN_B64: SET
• GOOGLE_CLIENT_ID: SET
```

## Common Issues

### Issue 1: Variables Not Showing After Adding

**Solution:**
- Refresh the page
- Make sure you clicked "Save Changes"
- Check if there's a "Sync" button that needs to be clicked

### Issue 2: Variables Set But Still Showing as NOT SET

**Causes:**
1. **Service not restarted** - Most common! You MUST restart after adding variables
2. **Wrong service** - Make sure you're setting variables on the correct service
3. **Typo in variable name** - Check for exact spelling (case-sensitive!)
4. **Variables set in wrong environment** - Check if you have staging/production separation

**Solution:**
1. Double-check variable names are EXACTLY:
   - `GOOGLE_OAUTH2_TOKEN_B64` (all caps, underscores)
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
2. Restart the service
3. Verify using debug endpoint: `/debug/env/google`

### Issue 3: Token Has Quotes

If you accidentally added quotes around the token value:
1. Edit the variable
2. Remove the quotes
3. Save
4. Restart

### Issue 4: Multiple Services

If you have multiple services (web service, worker, etc.), make sure to set variables on the **correct service** (usually the web service).

## Quick Checklist

- [ ] All variables added in Render.com Environment section
- [ ] Variable names are EXACTLY correct (case-sensitive)
- [ ] No quotes around values
- [ ] Clicked "Save Changes"
- [ ] Service restarted/redeployed
- [ ] Deployment completed successfully
- [ ] Verified using `/debug/env/google` endpoint

## Testing After Setup

1. Create a calendar event via voice
2. Check logs for:
   ```
   • GOOGLE_OAUTH2_TOKEN_B64: SET
   ✅ Google Calendar service obtained
   ✅ Google Calendar event created successfully
   ```
3. Verify in database that `google_calendar_event_id` is set

## Need Help?

If variables still aren't working:
1. Use `/debug/env/google` to see what's actually available
2. Check Render.com deployment logs for any errors
3. Verify you're setting variables on the correct service
4. Make sure the service restart completed successfully

