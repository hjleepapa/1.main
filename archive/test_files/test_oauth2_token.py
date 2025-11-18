#!/usr/bin/env python3
"""
Test OAuth2 token loading and validation
"""

import os
import pickle
import base64
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def test_oauth2_token():
    """Test OAuth2 token loading and validation"""
    
    print("🔧 Testing OAuth2 token...")
    
    # Check environment variables
    print("📋 Environment Variables:")
    print(f"• GOOGLE_OAUTH2_TOKEN_B64: {'✅ SET' if os.getenv('GOOGLE_OAUTH2_TOKEN_B64') else '❌ NOT SET'}")
    print(f"• GOOGLE_CLIENT_ID: {'✅ SET' if os.getenv('GOOGLE_CLIENT_ID') else '❌ NOT SET'}")
    print(f"• GOOGLE_CLIENT_SECRET: {'✅ SET' if os.getenv('GOOGLE_CLIENT_SECRET') else '❌ NOT SET'}")
    print()
    
    # Test OAuth2 token loading
    creds = None
    
    if os.getenv('GOOGLE_OAUTH2_TOKEN_B64'):
        print("🔧 Testing OAuth2 token loading from environment...")
        try:
            token_data = base64.b64decode(os.getenv('GOOGLE_OAUTH2_TOKEN_B64'))
            print(f"✅ Token data decoded, length: {len(token_data)} bytes")
            
            creds = pickle.loads(token_data)
            print(f"✅ Credentials loaded: valid={creds.valid}, expired={creds.expired}")
            print(f"✅ Has refresh token: {bool(creds.refresh_token)}")
            
        except Exception as e:
            print(f"❌ Error loading OAuth2 token from environment: {e}")
            creds = None
    
    elif os.path.exists('token.pickle'):
        print("🔧 Testing OAuth2 token loading from local file...")
        try:
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
            print(f"✅ Credentials loaded from file: valid={creds.valid}, expired={creds.expired}")
            print(f"✅ Has refresh token: {bool(creds.refresh_token)}")
            
        except Exception as e:
            print(f"❌ Error loading OAuth2 token from file: {e}")
            creds = None
    
    if creds:
        # Handle token refresh if needed
        if creds.expired and creds.refresh_token:
            print("🔧 Token expired, attempting refresh...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully")
            except Exception as refresh_error:
                print(f"❌ Token refresh failed: {refresh_error}")
                return False
        
        if not creds.valid:
            print("❌ OAuth2 token is not valid after loading/refresh")
            return False
        
        # Test Google Calendar service creation
        print("🔧 Testing Google Calendar service creation...")
        service = build('calendar', 'v3', credentials=creds)
        print("✅ Google Calendar service created successfully")
        
        # Test calendar list
        print("🔧 Testing calendar list...")
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        print(f"✅ Found {len(calendars)} calendars")
        
        for cal in calendars:
            print(f"  - {cal.get('summary', 'Unknown')} (ID: {cal.get('id', 'Unknown')}) - Primary: {cal.get('primary', False)}")
        
        return True
    else:
        print("❌ No OAuth2 token found in environment or local file")
        return False

if __name__ == "__main__":
    success = test_oauth2_token()
    if success:
        print("\n✅ OAuth2 token test successful!")
    else:
        print("\n❌ OAuth2 token test failed!")
