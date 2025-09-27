#!/usr/bin/env python3
"""
Test Sambanova WebSocket endpoints on hjlees.com
"""

import asyncio
import websockets
import ssl
import requests

async def test_sambanova_websocket():
    """Test Sambanova WebSocket endpoints."""
    
    test_urls = [
        "wss://hjlees.com",
        "wss://hjlees.com/ws", 
        "wss://hjlees.com/sambanova_todo",
        "wss://hjlees.com/sambanova_todo/ws",
        "wss://hjlees.com/sambanova_todo/twilio/ws",
    ]
    
    print("🔍 Testing Sambanova WebSocket Endpoints on hjlees.com")
    print("=" * 60)
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        try:
            websocket = await websockets.connect(
                url, 
                ssl=ssl_context,
                timeout=5
            )
            print("   ✅ WebSocket connection successful!")
            await websocket.close()
            return True
            
        except websockets.exceptions.InvalidHandshake as e:
            print(f"   ❌ WebSocket handshake failed: {e}")
        except ConnectionRefusedError as e:
            print(f"   ❌ Connection refused: {e}")
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
    
    return False

def test_http_endpoints():
    """Test HTTP endpoints for WebSocket upgrade headers."""
    print("\n🌐 Testing HTTP Endpoints for WebSocket Support")
    print("-" * 50)
    
    test_urls = [
        "https://hjlees.com",
        "https://hjlees.com/sambanova_todo",
        "https://hjlees.com/sambanova_todo/ws",
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"\n{url}")
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            # Check for WebSocket-related headers
            upgrade_header = response.headers.get('upgrade', '')
            connection_header = response.headers.get('connection', '')
            
            if 'websocket' in upgrade_header.lower():
                print(f"   🔌 WebSocket Upgrade: {upgrade_header}")
            if 'upgrade' in connection_header.lower():
                print(f"   🔌 Connection Upgrade: {connection_header}")
                
        except Exception as e:
            print(f"   ❌ HTTP request failed: {e}")

async def main():
    """Main test function."""
    print("🚀 Testing hjlees.com WebSocket After Code Update")
    print("=" * 60)
    
    # Test HTTP endpoints first
    test_http_endpoints()
    
    # Test WebSocket connections
    websocket_works = await test_sambanova_websocket()
    
    print("\n" + "=" * 60)
    print("📋 FINAL RESULTS:")
    print("=" * 60)
    
    if websocket_works:
        print("✅ WebSocket is now working on hjlees.com!")
        print("   → Twilio Media Streams should work")
        print("   → Real-time audio streaming available")
        print("   → Update Twilio config to use WebSocket")
    else:
        print("❌ WebSocket still not working on hjlees.com")
        print("   → Check if ASGI server is running")
        print("   → Verify Cloudflare WebSocket settings")
        print("   → Use HTTP-only mode for Twilio")

if __name__ == "__main__":
    asyncio.run(main())
