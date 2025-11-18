#!/usr/bin/env python3
"""
Simple WebSocket test for hjlees.com
"""

import asyncio
import websockets
import ssl

async def test_websocket():
    """Test WebSocket connection to hjlees.com"""
    url = "wss://hjlees.com"
    
    print(f"Testing WebSocket connection to: {url}")
    
    try:
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Try to connect
        websocket = await websockets.connect(url, ssl=ssl_context)
        print("✅ WebSocket connection successful!")
        await websocket.close()
        return True
        
    except websockets.exceptions.InvalidHandshake as e:
        print(f"❌ WebSocket handshake failed: {e}")
        print("   This usually means the server doesn't support WebSockets")
        return False
    except ConnectionRefusedError as e:
        print(f"❌ Connection refused: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def main():
    print("🔍 Testing hjlees.com WebSocket Support")
    print("=" * 40)
    
    success = await test_websocket()
    
    print("\n📋 Results:")
    if success:
        print("✅ hjlees.com supports WebSocket connections")
        print("   → You can use WebSocket for Twilio Media Streams")
    else:
        print("❌ hjlees.com does not support WebSocket connections")
        print("   → Use HTTP-only webhooks for Twilio")
        print("   → No real-time audio streaming available")
        print("   → Consider using ngrok for local development with WebSocket")

if __name__ == "__main__":
    asyncio.run(main())
