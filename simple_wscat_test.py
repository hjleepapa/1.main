#!/usr/bin/env python3
"""
Simple WebSocket test using wscat if available
"""

import subprocess
import sys

def test_with_wscat():
    """Test WebSocket using wscat command line tool."""
    print("🔍 Testing WebSocket with wscat...")
    
    # Check if wscat is available
    try:
        result = subprocess.run(['which', 'wscat'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ wscat not found. Install with: npm install -g wscat")
            return False
    except:
        print("❌ wscat not found. Install with: npm install -g wscat")
        return False
    
    # Test WebSocket connection
    test_urls = [
        "wss://hjlees.com",
        "wss://hjlees.com/convonet_todo/ws",
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        try:
            # Run wscat with timeout
            result = subprocess.run(
                ['wscat', '-c', url, '-w', '3'],  # 3 second wait
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("   ✅ WebSocket connection successful!")
                return True
            else:
                print(f"   ❌ Connection failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("   ❌ Connection timeout")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return False

def test_with_curl():
    """Test WebSocket upgrade with curl."""
    print("\n🔍 Testing WebSocket upgrade headers...")
    
    try:
        result = subprocess.run([
            'curl', '-I', '-H', 'Upgrade: websocket', '-H', 'Connection: Upgrade',
            'https://hjlees.com/convonet_todo/ws'
        ], capture_output=True, text=True, timeout=10)
        
        print(f"Response:\n{result.stdout}")
        
        if '101' in result.stdout:
            print("   ✅ WebSocket upgrade supported!")
            return True
        elif '404' in result.stdout:
            print("   ❌ WebSocket endpoint not found (404)")
        elif '400' in result.stdout:
            print("   ❌ WebSocket upgrade rejected (400)")
        else:
            print("   ❌ WebSocket upgrade not supported")
            
    except Exception as e:
        print(f"   ❌ Error testing upgrade: {e}")
    
    return False

def main():
    print("🚀 Simple WebSocket Test for hjlees.com")
    print("=" * 50)
    
    # Test with curl first
    curl_works = test_with_curl()
    
    # Test with wscat if available
    wscat_works = test_with_wscat()
    
    print("\n" + "=" * 50)
    print("📋 RESULTS:")
    print("=" * 50)
    
    if wscat_works:
        print("✅ WebSocket is working!")
    elif curl_works:
        print("✅ WebSocket upgrade supported!")
    else:
        print("❌ WebSocket still not working")
        print("   → Server is still running Gunicorn (WSGI)")
        print("   → Need to switch to ASGI server (Uvicorn)")
        print("   → Or enable WebSocket in current setup")

if __name__ == "__main__":
    main()
