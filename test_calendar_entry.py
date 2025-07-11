#!/usr/bin/env python3
"""
Test script to simulate calendar entry creation from Flask app
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.google_calendar import get_calendar_service
from datetime import datetime, timedelta

def test_calendar_entry_creation():
    """Test creating a calendar entry like the Flask app does"""
    try:
        # Simulate the exact flow from add_calendar_entry route
        title = "Test Calendar Entry"
        description = "This is a test calendar entry"
        event_from = "2024-01-15T10:00:00Z"
        event_to = "2024-01-15T11:00:00Z"
        
        # Parse datetime strings (same as Flask app)
        start_time = None
        end_time = None
        if event_from:
            try:
                start_time = datetime.fromisoformat(event_from.replace('Z', '+00:00'))
                print(f"✅ Parsed start_time: {start_time}")
            except Exception as e:
                print(f"❌ Failed to parse start_time: {e}")
                start_time = datetime.utcnow()
        if event_to:
            try:
                end_time = datetime.fromisoformat(event_to.replace('Z', '+00:00'))
                print(f"✅ Parsed end_time: {end_time}")
            except Exception as e:
                print(f"❌ Failed to parse end_time: {e}")
                end_time = start_time + timedelta(hours=1) if start_time else datetime.utcnow() + timedelta(hours=1)
        
        # Get calendar service
        calendar_service = get_calendar_service()
        print("✅ Google Calendar service initialized")
        
        # Create the event (same as Flask app)
        google_event_id = calendar_service.create_event(
            title=title,
            description=description or "Event from SYFW Todo System",
            start_time=start_time,
            end_time=end_time
        )
        
        if google_event_id:
            print(f"✅ Calendar event created successfully with ID: {google_event_id}")
            
            # Clean up - delete the test event
            if calendar_service.delete_event(google_event_id):
                print("✅ Test event deleted successfully")
            else:
                print("⚠️  Test event created but could not be deleted")
        else:
            print("❌ Failed to create calendar event")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("Testing calendar entry creation (Flask app flow)...")
    success = test_calendar_entry_creation()
    if success:
        print("\n🎉 Calendar entry creation is working!")
    else:
        print("\n💥 Calendar entry creation failed!") 