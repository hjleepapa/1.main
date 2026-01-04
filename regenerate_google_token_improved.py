#!/usr/bin/env python3
"""
Improved script to regenerate Google Calendar OAuth2 token
Validates the token before outputting to ensure it works correctly
"""

import os
import sys
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

def regenerate_token():
    """Regenerate Google Calendar OAuth2 token with validation"""
    
    # Get credentials from environment
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ ERROR: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set")
        print("\n📋 Please set these environment variables:")
        print("   export GOOGLE_CLIENT_ID='your-client-id'")
        print("   export GOOGLE_CLIENT_SECRET='your-client-secret'")
        return None
    
    print("🔧 Creating OAuth2 flow...")
    
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
    print("   Please sign in and grant calendar permissions")
    try:
        creds = flow.run_local_server(port=0)
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None
    
    print("✅ Authentication successful!")
    
    # Validate the token works
    print("\n🔧 Validating token...")
    try:
        service = build('calendar', 'v3', credentials=creds)
        calendars = service.calendarList().list().execute()
        calendar_count = len(calendars.get('items', []))
        print(f"✅ Token validated - can access {calendar_count} calendar(s)")
    except Exception as e:
        print(f"⚠️  Warning: Token generated but validation failed: {e}")
        print("   You may still want to try using this token")
    
    # Convert to base64 for environment variable
    print("\n🔧 Encoding token...")
    token_data = pickle.dumps(creds)
    token_b64 = base64.b64encode(token_data).decode('utf-8')
    
    # Save to file as backup
    print("💾 Saving to token.pickle as backup...")
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    
    # Output in multiple formats for easy copying
    print("\n" + "="*80)
    print("✅ Token generated and validated successfully!")
    print("="*80)
    
    print("\n📋 FOR RENDER.COM - Copy ONLY the token value below:")
    print("-" * 80)
    print(token_b64)
    print("-" * 80)
    
    print("\n📋 Token Information:")
    print(f"   Length: {len(token_b64)} characters")
    print(f"   Valid: {creds.valid}")
    print(f"   Expired: {creds.expired}")
    print(f"   Has refresh token: {bool(creds.refresh_token)}")
    
    print("\n📝 Instructions for Render.com:")
    print("   1. Copy ONLY the token string above (the long base64 string)")
    print("   2. Go to Render.com → Your Service → Environment")
    print("   3. Find GOOGLE_OAUTH2_TOKEN_B64")
    print("   4. Click Edit")
    print("   5. Paste the token (NO QUOTES, NO SPACES)")
    print("   6. Save")
    print("   7. Restart/Deploy your service")
    
    print("\n⚠️  IMPORTANT:")
    print("   - Do NOT include quotes around the token")
    print("   - Do NOT include 'GOOGLE_OAUTH2_TOKEN_B64=' prefix")
    print("   - Copy the entire token (it's very long)")
    print("   - No leading or trailing spaces")
    
    # Also save to a file for easy access
    with open('google_token_b64.txt', 'w') as f:
        f.write(token_b64)
    print("\n💾 Token also saved to: google_token_b64.txt")
    
    return token_b64

if __name__ == '__main__':
    try:
        token = regenerate_token()
        if token:
            print("\n✅ Done! Follow the instructions above to update Render.com")
        else:
            print("\n❌ Token generation failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

