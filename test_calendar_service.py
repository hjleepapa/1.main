#!/usr/bin/env python3
"""
Comprehensive test script to validate Google Calendar service functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.google_calendar import get_calendar_service
from datetime import datetime, timedelta
import time

def test_calendar_service():
    """Test all Google Calendar service functionality"""
    print("🧪 Testing Google Calendar Service...")
    print("=" * 50)
    
    # Test 1: Service Initialization
    print("\n1️⃣ Testing Service Initialization...")
    try:
        calendar_service = get_calendar_service()
        print("✅ Google Calendar service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize calendar service: {e}")
        return False
    
    # Test 2: Create Event
    print("\n2️⃣ Testing Event Creation...")
    test_title = "Test Event from SYFW Todo"
    test_description = "This is a test event created by the SYFW Todo system"
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)
    
    try:
        event_id = calendar_service.create_event(
            title=test_title,
            description=test_description,
            start_time=start_time,
            end_time=end_time
        )
        
        if event_id:
            print(f"✅ Event created successfully with ID: {event_id}")
            print(f"   Title: {test_title}")
            print(f"   Start: {start_time}")
            print(f"   End: {end_time}")
        else:
            print("❌ Event creation returned None")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create event: {e}")
        return False
    
    # Test 3: Get Event
    print("\n3️⃣ Testing Event Retrieval...")
    try:
        event = calendar_service.get_event(event_id)
        if event:
            print(f"✅ Event retrieved successfully")
            print(f"   Retrieved Title: {event.get('summary', 'N/A')}")
            print(f"   Retrieved Description: {event.get('description', 'N/A')}")
        else:
            print("❌ Failed to retrieve event")
            return False
    except Exception as e:
        print(f"❌ Failed to get event: {e}")
        return False
    
    # Test 4: Update Event
    print("\n4️⃣ Testing Event Update...")
    updated_title = "UPDATED: Test Event from SYFW Todo"
    updated_description = "This event has been updated by the test script"
    
    try:
        success = calendar_service.update_event(
            event_id=event_id,
            title=updated_title,
            description=updated_description
        )
        
        if success:
            print("✅ Event updated successfully")
            
            # Verify the update
            updated_event = calendar_service.get_event(event_id)
            if updated_event and updated_event.get('summary') == updated_title:
                print("✅ Update verification successful")
            else:
                print("⚠️  Update verification failed")
        else:
            print("❌ Failed to update event")
            return False
            
    except Exception as e:
        print(f"❌ Failed to update event: {e}")
        return False
    
    # Test 5: Delete Event
    print("\n5️⃣ Testing Event Deletion...")
    try:
        success = calendar_service.delete_event(event_id)
        if success:
            print("✅ Event deleted successfully")
            
            # Verify deletion
            deleted_event = calendar_service.get_event(event_id)
            if not deleted_event:
                print("✅ Deletion verification successful")
            else:
                print("⚠️  Deletion verification failed - event still exists")
        else:
            print("❌ Failed to delete event")
            return False
            
    except Exception as e:
        print(f"❌ Failed to delete event: {e}")
        return False
    
    # Test 6: Test with Different Time Formats
    print("\n6️⃣ Testing Different Time Formats...")
    try:
        # Test with timezone-aware datetime
        from datetime import timezone
        tz_start = datetime.now(timezone.utc) + timedelta(hours=2)
        tz_end = tz_start + timedelta(hours=1)
        
        tz_event_id = calendar_service.create_event(
            title="Timezone Test Event",
            description="Testing timezone-aware datetime",
            start_time=tz_start,
            end_time=tz_end,
            timezone='UTC'
        )
        
        if tz_event_id:
            print("✅ Timezone-aware event created successfully")
            # Clean up
            calendar_service.delete_event(tz_event_id)
            print("✅ Timezone test event cleaned up")
        else:
            print("❌ Failed to create timezone-aware event")
            
    except Exception as e:
        print(f"❌ Timezone test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 All Google Calendar service tests completed!")
    return True

def test_error_handling():
    """Test error handling scenarios"""
    print("\n🔍 Testing Error Handling...")
    print("=" * 30)
    
    calendar_service = get_calendar_service()
    
    # Test 1: Invalid event ID
    print("\n1️⃣ Testing Invalid Event ID...")
    try:
        result = calendar_service.get_event("invalid_event_id_12345")
        if result is None:
            print("✅ Correctly handled invalid event ID")
        else:
            print("⚠️  Unexpected result for invalid event ID")
    except Exception as e:
        print(f"✅ Correctly caught exception for invalid event ID: {e}")
    
    # Test 2: Update non-existent event
    print("\n2️⃣ Testing Update Non-existent Event...")
    try:
        success = calendar_service.update_event(
            event_id="non_existent_event_12345",
            title="This should fail"
        )
        if not success:
            print("✅ Correctly failed to update non-existent event")
        else:
            print("⚠️  Unexpectedly succeeded updating non-existent event")
    except Exception as e:
        print(f"✅ Correctly caught exception for non-existent event: {e}")
    
    # Test 3: Delete non-existent event
    print("\n3️⃣ Testing Delete Non-existent Event...")
    try:
        success = calendar_service.delete_event("non_existent_event_12345")
        if not success:
            print("✅ Correctly failed to delete non-existent event")
        else:
            print("⚠️  Unexpectedly succeeded deleting non-existent event")
    except Exception as e:
        print(f"✅ Correctly caught exception for non-existent event: {e}")

if __name__ == "__main__":
    print("🚀 Starting Google Calendar Service Validation...")
    
    # Run main tests
    main_success = test_calendar_service()
    
    # Run error handling tests
    test_error_handling()
    
    print("\n" + "=" * 50)
    if main_success:
        print("🎉 Google Calendar service is working correctly!")
        print("✅ You can now use it in your Flask application.")
    else:
        print("💥 Google Calendar service has issues!")
        print("❌ Check your credentials and permissions.")
    
    print("\n📝 Next steps:")
    print("1. If all tests passed, your calendar integration should work")
    print("2. Fix the database schema issue (missing google_calendar_event_id column)")
    print("3. Test your Flask endpoints again") 