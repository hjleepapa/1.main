#!/usr/bin/env python3
"""
Script to verify Google Calendar OAuth2 token status
Checks if the current token is valid and can access Google Calendar
"""

import os
import sys
import pickle
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def verify_token():
    """Verify Google Calendar OAuth2 token"""
    
    print("🔍 Checking Google Calendar OAuth2 token status...\n")
    
    # Check for token in environment
    token_b64 = os.getenv('GOOGLE_OAUTH2_TOKEN_B64')
    
    if not token_b64:
        print("❌ GOOGLE_OAUTH2_TOKEN_B64 environment variable not set")
        print("\n💡 Check your environment variables:")
        print("   - Render.com: Dashboard → Environment → Environment Variables")
        print("   - Local: Check your .env file")
        return False
    
    print(f"✅ Found GOOGLE_OAUTH2_TOKEN_B64 (length: {len(token_b64)} chars)")
    
    try:
        # Decode token
        print("🔧 Decoding token...")
        token_data = base64.b64decode(token_b64)
        creds = pickle.loads(token_data)
        print("✅ Token decoded successfully")
        
        # Check token status
        print(f"\n📊 Token Status:")
        print(f"   Valid: {creds.valid}")
        print(f"   Expired: {creds.expired}")
        print(f"   Has refresh_token: {bool(creds.refresh_token)}")
        
        # Try to refresh if expired
        if creds.expired and creds.refresh_token:
            print("\n🔄 Token expired, attempting refresh...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully!")
                print("\n⚠️  NOTE: Your environment variable still has the old token.")
                print("   Consider regenerating the token for long-term use.")
            except Exception as refresh_error:
                print(f"❌ Token refresh failed: {refresh_error}")
                print("\n💡 The refresh token may have expired.")
                print("   Solution: Regenerate token using regenerate_google_token.py")
                return False
        elif creds.expired and not creds.refresh_token:
            print("\n❌ Token expired and no refresh token available")
            print("   Solution: Regenerate token using regenerate_google_token.py")
            return False
        
        # Check if valid after refresh
        if not creds.valid:
            print("\n❌ Token is not valid")
            print("   Solution: Regenerate token using regenerate_google_token.py")
            return False
        
        # Test calendar access
        print("\n🔧 Testing Google Calendar API access...")
        service = build('calendar', 'v3', credentials=creds)
        
        try:
            calendars = service.calendarList().list().execute()
            calendar_count = len(calendars.get('items', []))
            print(f"✅ Successfully accessed Google Calendar API")
            print(f"   Found {calendar_count} calendar(s)")
            
            # Try to create a test event (optional - commented out by default)
            # Uncomment to test event creation
            # from datetime import datetime, timedelta, timezone
            # test_event = {
            #     'summary': 'Test Event - Delete Me',
            #     'description': 'This is a test event',
            #     'start': {
            #         'dateTime': datetime.now(timezone.utc).isoformat(),
            #         'timeZone': 'UTC',
            #     },
            #     'end': {
            #         'dateTime': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            #         'timeZone': 'UTC',
            #     },
            # }
            # event = service.events().insert(calendarId='primary', body=test_event).execute()
            # print(f"✅ Test event created: {event.get('id')}")
            
            print("\n" + "="*70)
            print("✅ Token is VALID and working correctly!")
            print("="*70)
            return True
            
        except HttpError as error:
            print(f"❌ Google Calendar API error: {error}")
            if error.resp.status == 401:
                print("   Authentication failed - token may be invalid")
            elif error.resp.status == 403:
                print("   Permission denied - check OAuth consent screen")
            return False
        
    except Exception as e:
        print(f"\n❌ Error processing token: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = verify_token()
    sys.exit(0 if success else 1)
