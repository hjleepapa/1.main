# Google Calendar Token "Signature has expired" - Debugging Guide

## Problem
After regenerating `GOOGLE_OAUTH2_TOKEN_B64` and updating it in Render.com, you're still getting:
```
⚠️  Token expired: Signature has expired
```

## Common Causes & Solutions

### 1. Environment Variable Formatting Issues (Most Common)

**Problem:** Extra spaces, line breaks, or quotes can break the token.

**Solution:**
1. When copying the token from the script output, make sure to copy ONLY the token value (no extra spaces before/after)
2. In Render.com, paste the token directly - don't add quotes around it
3. Verify the token length matches (should be several thousand characters)

**Check in Render.com:**
- Go to Environment → Environment Variables
- Find `GOOGLE_OAUTH2_TOKEN_B64`
- Verify it doesn't have quotes: `GOOGLE_OAUTH2_TOKEN_B64="token..."` ❌
- Should be: `GOOGLE_OAUTH2_TOKEN_B64=token...` ✅
- Verify no leading/trailing spaces

### 2. Application Not Restarted

**Problem:** Render.com application is still using the old cached token.

**Solution:**
1. Go to Render.com Dashboard
2. Find your service
3. Click **Manual Deploy** → **Clear build cache & deploy**
4. Or use **Restart** if available
5. Wait for deployment to complete

### 3. Token Generation Timing Issue

**Problem:** The token might have been generated but there's a time sync issue.

**Solution:**
1. Generate the token again using `regenerate_google_token.py`
2. Immediately copy and paste it to Render.com
3. Deploy/restart immediately after updating

### 4. Refresh Token Expired

**Problem:** Even though you generated a new token, the refresh token itself might be invalid.

**Solution:**
1. Check if you're using the correct Google account
2. Verify the OAuth consent screen is properly configured
3. Make sure you granted all required permissions
4. Try revoking access and re-authenticating:
   - Go to: https://myaccount.google.com/permissions
   - Find your app and revoke access
   - Run `regenerate_google_token.py` again

### 5. Clock Skew / Time Sync

**Problem:** Server time is significantly different from your local time.

**Solution:**
- This is usually handled automatically, but if persists, check Render.com server time
- Generate token close to deployment time

## Step-by-Step Debugging

### Step 1: Verify Token Format Locally

Run this to check your token before uploading:

```bash
# Set the token from your local generation
export GOOGLE_OAUTH2_TOKEN_B64="your-token-here"

# Run verification script
python3 verify_google_token.py
```

If this works locally, the token format is correct.

### Step 2: Verify Token Format in Render.com

Create a temporary endpoint to check the token (add to a test route):

```python
@convonet_todo_bp.route('/debug/google-token', methods=['GET'])
def debug_google_token():
    """Debug endpoint to check Google token status"""
    import os
    import base64
    import pickle
    
    token_b64 = os.getenv('GOOGLE_OAUTH2_TOKEN_B64', 'NOT_SET')
    
    if token_b64 == 'NOT_SET':
        return jsonify({
            'status': 'error',
            'message': 'GOOGLE_OAUTH2_TOKEN_B64 not set',
            'token_length': 0
        })
    
    try:
        token_data = base64.b64decode(token_b64)
        creds = pickle.loads(token_data)
        
        return jsonify({
            'status': 'success',
            'token_length': len(token_b64),
            'decoded_length': len(token_data),
            'valid': creds.valid if hasattr(creds, 'valid') else 'unknown',
            'expired': creds.expired if hasattr(creds, 'expired') else 'unknown',
            'has_refresh_token': bool(creds.refresh_token) if hasattr(creds, 'refresh_token') else False
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'token_length': len(token_b64)
        })
```

Then check: `https://your-domain.com/convonet_todo/debug/google-token`

### Step 3: Regenerate with Better Error Handling

Use this improved regeneration script that validates the token before output:

```bash
python3 regenerate_google_token.py
```

The script should output the token and verify it works before you copy it.

### Step 4: Update Render.com Correctly

1. **Copy the token carefully:**
   - Copy ONLY the token value (the long base64 string)
   - Don't include the `GOOGLE_OAUTH2_TOKEN_B64=` part
   - Don't include quotes

2. **In Render.com:**
   - Go to: Dashboard → Your Service → Environment
   - Find `GOOGLE_OAUTH2_TOKEN_B64`
   - Click Edit
   - Paste the token value directly (no quotes, no spaces)
   - Save

3. **Verify the format:**
   - After saving, the value should show as a long string
   - It should NOT have quotes around it in the UI
   - Check the length matches (usually 2000-4000+ characters)

### Step 5: Force Restart

1. Go to Render.com Dashboard
2. Your Service → Manual Deploy
3. Select "Clear build cache & deploy"
4. Wait for deployment

## Quick Fix Script

Run this locally to generate a fresh token and output it in a format ready for Render.com:

```bash
# Set your credentials
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"

# Generate token
python3 regenerate_google_token.py > token_output.txt

# The token will be in token_output.txt
# Copy JUST the token value (not the variable name)
```

## Alternative: Use Service Account (For Production)

If OAuth2 continues to be problematic, consider switching to Service Account authentication:

**Advantages:**
- No token expiration issues
- No user interaction required
- More reliable for server environments

**Setup:**
1. Google Cloud Console → APIs & Services → Credentials
2. Create Service Account
3. Download JSON key
4. Share your calendar with the service account email
5. Use `GOOGLE_CREDENTIALS_B64` instead of `GOOGLE_OAUTH2_TOKEN_B64`

## Verification Checklist

- [ ] Token was generated using the script (not manually)
- [ ] Token copied completely (full length, no truncation)
- [ ] No quotes added around token in Render.com
- [ ] No leading/trailing spaces
- [ ] Environment variable saved in Render.com
- [ ] Application restarted/redeployed after updating
- [ ] Token length matches expected (2000-4000+ chars)
- [ ] OAuth consent screen properly configured
- [ ] Correct Google account used for authentication

## Still Not Working?

1. Check Render.com logs for detailed error messages
2. Verify the token works locally using `verify_google_token.py`
3. Try revoking and re-authenticating (revoke at Google account permissions)
4. Consider using Service Account authentication instead
5. Check if there are multiple environment variable sets (staging vs production)

