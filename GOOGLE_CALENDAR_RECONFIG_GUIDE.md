# Google Calendar OAuth2 Reconfiguration Guide

## Problem
Google Calendar event IDs are not being created. This typically happens when OAuth2 tokens expire or credentials become invalid.

## Quick Diagnosis Checklist

### 1. Check Current Configuration

The system uses OAuth2 authentication via environment variables. Check if these are set:

**Required Environment Variables:**
- `GOOGLE_OAUTH2_TOKEN_B64` - Base64-encoded OAuth2 token (primary method)
- OR `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` - For generating new tokens

**Check in your deployment:**
```bash
# If using Render.com, check Environment variables in dashboard
# If using local .env file, check these variables exist
```

### 2. Common Causes

1. **Token Expired** - OAuth2 access tokens expire after 1 hour
2. **Refresh Token Expired/Revoked** - Refresh tokens can expire after 6 months of inactivity
3. **Credentials Invalid** - Client ID/Secret may have been regenerated
4. **Token Not Refreshing** - Refresh mechanism may have failed

---

## Solution: Reconfigure Google Calendar OAuth2

### Option 1: Regenerate Token Using Existing Credentials (Recommended)

If you have `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` set, you can regenerate the token locally:

#### Step 1: Create a Token Generation Script

Create a file `regenerate_google_token.py` in your project root:

```python
import os
import pickle
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

def regenerate_token():
    """Regenerate Google Calendar OAuth2 token"""
    
    # Get credentials from environment or create config
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set")
        return None
    
    # Create OAuth2 flow configuration
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    # Create flow
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    
    # Run local server to authenticate (opens browser)
    print("🌐 Opening browser for authentication...")
    creds = flow.run_local_server(port=0)
    
    # Convert to base64 for environment variable
    token_data = pickle.dumps(creds)
    token_b64 = base64.b64encode(token_data).decode('utf-8')
    
    print("\n✅ Token generated successfully!")
    print("\n📋 Add this to your environment variables:")
    print(f"GOOGLE_OAUTH2_TOKEN_B64={token_b64}")
    print("\n💾 Also saving to token.pickle as backup...")
    
    # Save to file as backup
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    
    return token_b64

if __name__ == '__main__':
    token = regenerate_token()
    if token:
        print(f"\n✅ Token length: {len(token)} characters")
        print("✅ Copy the GOOGLE_OAUTH2_TOKEN_B64 value above to your environment variables")
```

#### Step 2: Run the Script

```bash
# Set your client credentials
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"

# Run the script
python3 regenerate_google_token.py
```

This will:
1. Open a browser window
2. Ask you to sign in to Google
3. Request calendar permissions
4. Generate a new token
5. Output the base64-encoded token for your environment variable

#### Step 3: Update Environment Variable

Copy the generated `GOOGLE_OAUTH2_TOKEN_B64` value and:
- **Render.com**: Add/update in Environment Variables section
- **Local .env**: Update the variable in your `.env` file
- **Server**: Export the variable or add to your environment config

#### Step 4: Restart Application

After updating the environment variable, restart your application so it picks up the new token.

---

### Option 2: Get New Google Cloud Credentials

If you don't have valid `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`, you need to create new ones:

#### Step 1: Go to Google Cloud Console

1. Visit: https://console.cloud.google.com/
2. Select your project (or create a new one)

#### Step 2: Enable Google Calendar API

1. Navigate to **APIs & Services** → **Library**
2. Search for "Google Calendar API"
3. Click **Enable**

#### Step 3: Create OAuth 2.0 Credentials

1. Navigate to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. If prompted, configure OAuth consent screen:
   - User Type: **External** (or Internal if using Google Workspace)
   - App name: Your app name
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `https://www.googleapis.com/auth/calendar`
   - Test users: Add your Google account email
4. Application type: **Desktop app**
5. Name: "Convonet Calendar Client"
6. Click **Create**
7. Download the credentials JSON file (or copy Client ID and Secret)

#### Step 4: Extract Client ID and Secret

From the downloaded JSON or the credentials page:

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

Set these as environment variables:
```bash
GOOGLE_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

#### Step 5: Generate Token

Use Option 1 (above) to generate a token with the new credentials.

---

## Verification Steps

### 1. Check if Token is Valid

Test the token by creating a simple test script:

```python
import os
import pickle
import base64
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Load token from environment
token_b64 = os.getenv('GOOGLE_OAUTH2_TOKEN_B64')
if token_b64:
    token_data = base64.b64decode(token_b64)
    creds = pickle.loads(token_data)
    
    # Check if expired and refresh if needed
    if creds.expired and creds.refresh_token:
        print("🔄 Token expired, refreshing...")
        creds.refresh(Request())
        print("✅ Token refreshed")
    
    if creds.valid:
        print("✅ Token is valid")
        
        # Test calendar service
        service = build('calendar', 'v3', credentials=creds)
        calendars = service.calendarList().list().execute()
        print(f"✅ Can access {len(calendars.get('items', []))} calendars")
    else:
        print("❌ Token is not valid - needs regeneration")
else:
    print("❌ GOOGLE_OAUTH2_TOKEN_B64 not set")
```

### 2. Test Calendar Event Creation

```python
from shared.google_calendar import get_calendar_service
from datetime import datetime, timedelta, timezone

# Test creating an event
service = get_calendar_service()
start_time = datetime.now(timezone.utc)
end_time = start_time + timedelta(hours=1)

event_id = service.create_event(
    title="Test Event",
    description="Testing Google Calendar integration",
    start_time=start_time,
    end_time=end_time
)

if event_id:
    print(f"✅ Event created successfully: {event_id}")
else:
    print("❌ Failed to create event")
```

---

## Troubleshooting

### Issue: "Token refresh failed"

**Cause:** Refresh token has expired or been revoked.

**Solution:** Regenerate token using Option 1 or Option 2 above.

### Issue: "Invalid credentials"

**Cause:** Client ID or Secret is incorrect.

**Solution:** 
1. Verify credentials in Google Cloud Console
2. Check environment variables are set correctly
3. Regenerate credentials if needed (Option 2)

### Issue: "Access denied" or "Insufficient permissions"

**Cause:** OAuth consent screen not configured or scopes not granted.

**Solution:**
1. Go to Google Cloud Console → APIs & Services → OAuth consent screen
2. Ensure Calendar API scope is added: `https://www.googleapis.com/auth/calendar`
3. If in testing phase, add your email to "Test users"
4. Re-authenticate to grant permissions

### Issue: Token works locally but not in production

**Cause:** Environment variable not set correctly in production.

**Solution:**
1. Verify `GOOGLE_OAUTH2_TOKEN_B64` is set in production environment
2. Check for encoding issues (should be base64)
3. Ensure no extra whitespace or quotes
4. Restart application after updating

### Issue: Browser doesn't open for authentication

**Cause:** Running in headless/server environment.

**Solution:**
1. Run token generation script on local machine (not server)
2. Copy generated token to server environment variables
3. Or use service account credentials for server environments (different setup)

---

## Alternative: Service Account (For Server Environments)

For production servers where browser-based OAuth2 is not practical, consider using a Service Account:

### Benefits:
- No user interaction required
- Tokens don't expire (long-lived)
- Better for server/automated environments

### Setup:
1. Google Cloud Console → APIs & Services → Credentials
2. Create Credentials → Service Account
3. Download JSON key file
4. Share calendar with service account email
5. Use service account credentials instead of OAuth2

(Note: This requires code changes to use service account authentication)

---

## Troubleshooting: "Signature has expired" Error

If you get this error even after regenerating the token:

### Common Causes:

1. **Environment Variable Formatting**
   - Make sure there are NO quotes around the token value in Render.com
   - No leading/trailing spaces
   - Copy the ENTIRE token (it's very long, 2000-4000+ characters)

2. **Application Not Restarted**
   - After updating the environment variable, you MUST restart/redeploy
   - In Render.com: Manual Deploy → Clear build cache & deploy

3. **Token Not Fully Copied**
   - The token is very long - make sure you copied the entire value
   - Check token length matches expected (use `verify_google_token.py`)

4. **Refresh Token Issue**
   - Try revoking access at https://myaccount.google.com/permissions
   - Then regenerate the token

See `GOOGLE_CALENDAR_TOKEN_DEBUG.md` for detailed debugging steps.

---

## Quick Reference: Environment Variables

```bash
# Primary method (recommended)
GOOGLE_OAUTH2_TOKEN_B64=base64-encoded-pickle-token

# Alternative: For token generation
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# For service account (different approach)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

---

## Need Help?

1. Check application logs for specific error messages
2. Verify environment variables are set correctly
3. Test token validity using verification script
4. Check Google Cloud Console for credential status
5. Review OAuth consent screen configuration

---

**Last Updated:** 2025-01-XX  
**Related Files:**
- `shared/google_calendar.py` - Calendar service implementation
- `convonet/mcps/local_servers/db_todo.py` - OAuth2 authentication code
- `CONVONET_DEPLOYMENT_CONFIG.md` - General deployment configuration

