#!/usr/bin/env python3
"""
Test script to verify Google Calendar integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.google_calendar import get_calendar_service
from datetime import datetime, timedelta

def test_calendar_integration():
    """Test creating a calendar event"""
    try:
        # Get calendar service
        calendar_service = get_calendar_service()
        print("✅ Google Calendar service initialized successfully")
        
        # Create a test event
        test_title = "Test Event from SYFW Todo"
        test_description = "This is a test event created by the SYFW Todo system"
        start_time = datetime.utcnow() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        
        # Create the event
        event_id = calendar_service.create_event(
            title=test_title,
            description=test_description,
            start_time=start_time,
            end_time=end_time
        )
        
        if event_id:
            print(f"✅ Test event created successfully with ID: {event_id}")
            
            # Clean up - delete the test event
            if calendar_service.delete_event(event_id):
                print("✅ Test event deleted successfully")
            else:
                print("⚠️  Test event created but could not be deleted")
        else:
            print("❌ Failed to create test event")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing Google Calendar integration...")
    success = test_calendar_integration()
    if success:
        print("\n🎉 Google Calendar integration is working!")
    else:
        print("\n💥 Google Calendar integration failed!") 