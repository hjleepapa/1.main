# Quick Fix: Render.com Token Format Issues

## Most Likely Problem

The token in Render.com likely has formatting issues. Here's how to fix it:

## Step-by-Step Fix

### 1. Generate a Fresh Token Locally

```bash
# Use the improved script
python3 regenerate_google_token_improved.py
```

This will:
- Validate the token works
- Output it in a clear format
- Save it to `google_token_b64.txt` for easy copying

### 2. Copy the Token Correctly

**IMPORTANT:** Copy ONLY the token value:
- Open `google_token_b64.txt` 
- Copy the entire content (it's one very long line)
- Do NOT add quotes
- Do NOT add spaces before/after
- Make sure you copied the ENTIRE token (it's 2000-4000+ characters)

### 3. Update Render.com

1. Go to: https://dashboard.render.com/
2. Navigate to your service
3. Click **Environment** (left sidebar)
4. Find `GOOGLE_OAUTH2_TOKEN_B64`
5. Click **Edit** (pencil icon)
6. **DELETE the entire current value**
7. **Paste the new token** (just the token, no quotes, no spaces)
8. Click **Save**

### 4. Verify the Format

After saving, check that:
- The value shows as a long string (not wrapped in quotes)
- No `"` quotes visible in the UI
- The length looks correct (very long string)

### 5. Force Restart

1. In Render.com, go to **Manual Deploy**
2. Select **Clear build cache & deploy**
3. Wait for deployment to complete
4. Check logs for any errors

## Common Mistakes to Avoid

❌ **WRONG:**
```
GOOGLE_OAUTH2_TOKEN_B64="eyJhbGc..."
```
(With quotes)

❌ **WRONG:**
```
GOOGLE_OAUTH2_TOKEN_B64 = eyJhbGc...
```
(With spaces around =)

❌ **WRONG:**
```
GOOGLE_OAUTH2_TOKEN_B64=eyJhbGc... (truncated)
```
(Not fully copied)

✅ **CORRECT:**
```
GOOGLE_OAUTH2_TOKEN_B64=eyJhbGciOiJSUzI1NiIsImtpZCI6Ij... (full long string)
```
(No quotes, no spaces, full token)

## Verify It Works

After deployment, check the logs for:
- ✅ "Token refreshed successfully" - Good!
- ❌ "Token expired" or "Signature has expired" - Still wrong format

## Still Not Working?

1. Try revoking access at https://myaccount.google.com/permissions
2. Generate a completely fresh token
3. Make sure you're using the improved script (`regenerate_google_token_improved.py`)
4. Consider using Service Account authentication (more reliable for servers)

