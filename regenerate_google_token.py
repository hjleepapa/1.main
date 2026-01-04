#!/usr/bin/env python3
"""
Script to regenerate Google Calendar OAuth2 token
Run this locally to generate a new token when the current one expires
"""

import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']

def regenerate_token():
    """Regenerate Google Calendar OAuth2 token"""
    
    # Get credentials from environment
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ ERROR: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set")
        print("\n📋 Please set these environment variables:")
        print("   export GOOGLE_CLIENT_ID='your-client-id'")
        print("   export GOOGLE_CLIENT_SECRET='your-client-secret'")
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
    print("🔧 Creating OAuth2 flow...")
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    
    # Run local server to authenticate (opens browser)
    print("🌐 Opening browser for authentication...")
    print("   Please sign in and grant calendar permissions")
    creds = flow.run_local_server(port=0)
    
    # Convert to base64 for environment variable
    token_data = pickle.dumps(creds)
    token_b64 = base64.b64encode(token_data).decode('utf-8')
    
    print("\n" + "="*70)
    print("✅ Token generated successfully!")
    print("="*70)
    print("\n📋 Add this to your environment variables:")
    print(f"\nGOOGLE_OAUTH2_TOKEN_B64={token_b64}\n")
    print("\n💾 Also saving to token.pickle as backup...")
    
    # Save to file as backup
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    print("✅ Saved to token.pickle")
    
    return token_b64

if __name__ == '__main__':
    try:
        token = regenerate_token()
        if token:
            print(f"\n✅ Token length: {len(token)} characters")
            print("\n📝 Next steps:")
            print("   1. Copy the GOOGLE_OAUTH2_TOKEN_B64 value above")
            print("   2. Add it to your environment variables (Render.com, .env file, etc.)")
            print("   3. Restart your application")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
