#!/usr/bin/env python3
"""
Generate OAuth2 token for Google Calendar using client credentials.
This script will create a token.pickle file that can be used for authentication.
"""

import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes for Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def generate_oauth2_token():
    """Generate OAuth2 token using client credentials"""
    
    # Get client credentials from environment or user input
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("Please provide your OAuth2 client credentials:")
        client_id = input("Client ID: ").strip()
        client_secret = input("Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Client ID and Client Secret are required")
        return
    
    print("🔧 Generating OAuth2 token...")
    
    # Create client configuration
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
    
    # Create OAuth2 flow
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    
    # Run the OAuth2 flow
    print("🌐 Opening browser for OAuth2 authentication...")
    print("Please complete the authentication in your browser.")
    
    creds = flow.run_local_server(port=0)
    
    # Save credentials to token.pickle
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    
    print("✅ OAuth2 token saved to token.pickle")
    
    # Generate base64 encoded token for Render.com
    with open('token.pickle', 'rb') as token:
        token_data = token.read()
    
    token_b64 = base64.b64encode(token_data).decode('utf-8')
    
    print("\n" + "="*80)
    print("GOOGLE_OAUTH2_TOKEN_B64 Environment Variable for Render.com:")
    print("="*80)
    print()
    print("Copy this entire value and paste it as GOOGLE_OAUTH2_TOKEN_B64 in your Render.com environment variables:")
    print()
    print(token_b64)
    print()
    print("="*80)
    print("Instructions:")
    print("1. Go to your Render.com dashboard")
    print("2. Select your service")
    print("3. Go to Environment tab")
    print("4. Add new environment variable:")
    print("   Key: GOOGLE_OAUTH2_TOKEN_B64")
    print("   Value: [paste the long string above]")
    print("5. Save and redeploy")
    print("="*80)
    
    # Also save client credentials for reference
    client_creds = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    print("\n📋 Your OAuth2 Client Credentials:")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret}")
    print("\n💡 You can also add these as environment variables:")
    print("GOOGLE_CLIENT_ID=<your_client_id>")
    print("GOOGLE_CLIENT_SECRET=<your_client_secret>")

if __name__ == "__main__":
    generate_oauth2_token()
