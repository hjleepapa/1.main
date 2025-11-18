#!/usr/bin/env python3
"""
Test script to check WebSocket capability on hjlees.com
"""

import asyncio
import websockets
import ssl
import requests
import socket
from urllib.parse import urlparse

async def test_websocket_connection(url):
    """Test WebSocket connection to a given URL."""
    print(f"🔍 Testing WebSocket connection to: {url}")
    
    try:
        # Parse the URL
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'wss' else 80)
        
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Scheme: {parsed.scheme}")
        
        # Create SSL context for wss connections
        ssl_context = None
        if parsed.scheme == 'wss':
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        # Test WebSocket connection
        async with websockets.connect(
            url, 
            ssl=ssl_context,
            timeout=10,
            ping_interval=None,
            ping_timeout=None
        ) as websocket:
            print(f"   ✅ WebSocket connection successful!")
            
            # Test sending a message
            await websocket.send("test message")
            print(f"   ✅ Message sent successfully")
            
            # Try to receive a response (with timeout)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"   ✅ Response received: {response}")
            except asyncio.TimeoutError:
                print(f"   ⚠️  No response received (timeout)")
            
            return True
            
    except websockets.exceptions.InvalidURI as e:
        print(f"   ❌ Invalid URI: {e}")
        return False
    except websockets.exceptions.ConnectionClosed as e:
        print(f"   ❌ Connection closed: {e}")
        return False
    except websockets.exceptions.InvalidHandshake as e:
        print(f"   ❌ Invalid handshake: {e}")
        return False
    except ConnectionRefusedError as e:
        print(f"   ❌ Connection refused: {e}")
        return False
    except socket.gaierror as e:
        print(f"   ❌ DNS resolution failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_http_endpoint(url):
    """Test HTTP endpoint accessibility."""
    print(f"🌐 Testing HTTP endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"   ✅ HTTP response: {response.status_code}")
        print(f"   📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        # Check for WebSocket upgrade headers
        if 'upgrade' in response.headers:
            print(f"   🔌 Upgrade header found: {response.headers['upgrade']}")
        
        return True
        
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"   ❌ Timeout: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request error: {e}")
        return False

def test_dns_resolution(hostname):
    """Test DNS resolution for hostname."""
    print(f"🔍 Testing DNS resolution for: {hostname}")
    
    try:
        ip_addresses = socket.getaddrinfo(hostname, None)
        print(f"   ✅ DNS resolution successful:")
        for addr in ip_addresses:
            print(f"      {addr[4][0]} ({addr[1].name})")
        return True
    except socket.gaierror as e:
        print(f"   ❌ DNS resolution failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Testing hjlees.com WebSocket Capability")
    print("=" * 60)
    
    # Test URLs to check
    test_urls = [
        "https://hjlees.com",
        "wss://hjlees.com",
        "wss://hjlees.com/ws",
        "wss://hjlees.com/convonet_todo/ws",
        "ws://hjlees.com",  # Non-SSL version
    ]
    
    results = {}
    
    # Test DNS resolution first
    print("1. DNS Resolution Test")
    print("-" * 30)
    dns_ok = test_dns_resolution("hjlees.com")
    print()
    
    if not dns_ok:
        print("❌ DNS resolution failed. Cannot proceed with WebSocket tests.")
        return
    
    # Test HTTP endpoints
    print("2. HTTP Endpoint Tests")
    print("-" * 30)
    for url in test_urls:
        if url.startswith("https://"):
            results[url] = test_http_endpoint(url)
    print()
    
    # Test WebSocket connections
    print("3. WebSocket Connection Tests")
    print("-" * 30)
    for url in test_urls:
        if url.startswith("ws"):
            results[url] = await test_websocket_connection(url)
    print()
    
    # Summary
    print("4. Test Summary")
    print("-" * 30)
    for url, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {url}")
    
    # Recommendations
    print("\n5. Recommendations")
    print("-" * 30)
    
    if results.get("https://hjlees.com", False):
        print("✅ hjlees.com is accessible via HTTPS")
    else:
        print("❌ hjlees.com HTTPS access failed")
    
    if results.get("wss://hjlees.com", False):
        print("✅ hjlees.com supports WebSocket connections")
        print("   → You can use WebSocket endpoints")
    else:
        print("❌ hjlees.com does not support WebSocket connections")
        print("   → You may need to use HTTP-only webhooks")
        print("   → Or configure WebSocket support on hjlees.com")
    
    # Alternative approaches
    print("\n6. Alternative Approaches")
    print("-" * 30)
    print("If WebSocket is not supported:")
    print("   → Use HTTP webhooks only (no real-time audio streaming)")
    print("   → Configure Twilio to use voice-only mode")
    print("   → Implement polling-based audio processing")
    print("   → Consider using a WebSocket-capable hosting service")

if __name__ == "__main__":
    asyncio.run(main())
