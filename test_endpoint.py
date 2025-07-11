#!/usr/bin/env python3
"""
Test script to call the Flask endpoint directly
"""
import requests
import json

def test_calendar_endpoint():
    """Test the add_calendar_entry endpoint directly"""
    
    # Test data - correct format
    test_data = {
        "message": {
            "toolCalls": [
                {
                    "id": "test_call_123",
                    "function": {
                        "name": "addCalendarEntry",
                        "arguments": {
                            "title": "Test Calendar Event via Endpoint",
                            "description": "This is a test event created by calling the endpoint directly",
                            "event_from": "2024-01-15T14:00:00Z",
                            "event_to": "2024-01-15T15:00:00Z"
                        }
                    }
                }
            ]
        }
    }
    
    try:
        # Make the request
        response = requests.post(
            'http://localhost:5000/syfw_todo/add_calendar_entry',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Endpoint call successful!")
        else:
            print("❌ Endpoint call failed!")
            
    except Exception as e:
        print(f"❌ Error calling endpoint: {e}")

if __name__ == "__main__":
    print("Testing Flask endpoint directly...")
    test_calendar_endpoint() 