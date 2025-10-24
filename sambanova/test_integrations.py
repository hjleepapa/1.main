#!/usr/bin/env python3
"""
Test script for Redis and Composio integrations
Run this to verify everything is working correctly
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_redis_connection():
    """Test Redis connection"""
    print("🔴 Testing Redis connection...")
    try:
        from sambanova.redis_manager import redis_manager
        
        if redis_manager.is_available():
            print("✅ Redis connection successful")
            
            # Test session operations
            test_session_id = "test_session_123"
            test_data = {
                'authenticated': 'True',
                'user_id': 'test_user',
                'user_name': 'Test User'
            }
            
            # Create session
            if redis_manager.create_session(test_session_id, test_data, ttl=60):
                print("✅ Session creation successful")
                
                # Get session
                retrieved_data = redis_manager.get_session(test_session_id)
                if retrieved_data and retrieved_data.get('user_id') == 'test_user':
                    print("✅ Session retrieval successful")
                else:
                    print("❌ Session retrieval failed")
                
                # Delete session
                if redis_manager.delete_session(test_session_id):
                    print("✅ Session deletion successful")
                else:
                    print("❌ Session deletion failed")
            else:
                print("❌ Session creation failed")
                
            return True
        else:
            print("❌ Redis connection failed - Redis unavailable")
            return False
            
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

def test_composio_connection():
    """Test Composio connection"""
    print("🔗 Testing Composio connection...")
    try:
        from sambanova.composio_tools import test_composio_connection, get_available_apps
        
        if test_composio_connection():
            print("✅ Composio connection successful")
            
            # Test getting available apps
            apps = get_available_apps()
            print(f"✅ Found {len(apps)} available apps: {apps[:5]}...")  # Show first 5
            
            return True
        else:
            print("❌ Composio connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Composio test failed: {e}")
        return False

def test_composio_tools():
    """Test Composio tools loading"""
    print("🔧 Testing Composio tools loading...")
    try:
        from sambanova.composio_tools import get_all_integration_tools
        
        tools = get_all_integration_tools()
        print(f"✅ Loaded {len(tools)} Composio tools")
        
        # Show tool names
        tool_names = [getattr(tool, 'name', str(tool)) for tool in tools[:5]]
        print(f"✅ Sample tools: {tool_names}")
        
        return True
        
    except Exception as e:
        print(f"❌ Composio tools test failed: {e}")
        return False

def test_webrtc_redis_integration():
    """Test WebRTC Redis integration"""
    print("🎤 Testing WebRTC Redis integration...")
    try:
        from sambanova.webrtc_voice_server import redis_manager
        
        if redis_manager.is_available():
            print("✅ WebRTC Redis integration working")
            return True
        else:
            print("⚠️ WebRTC using fallback storage (Redis unavailable)")
            return True  # This is acceptable fallback behavior
            
    except Exception as e:
        print(f"❌ WebRTC Redis integration test failed: {e}")
        return False

async def test_agent_integration():
    """Test agent with Composio tools"""
    print("🤖 Testing agent integration...")
    try:
        from sambanova.routes import _get_agent_graph
        
        # This will test the full agent initialization with Composio tools
        graph = await _get_agent_graph()
        print("✅ Agent graph with Composio tools loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Sambanova Integration Tests")
    print("=" * 50)
    
    # First, test environment configuration
    print("🔧 Testing environment configuration...")
    try:
        from sambanova.environment_config import config
        config.print_config_summary()
        print()
    except Exception as e:
        print(f"❌ Environment configuration test failed: {e}")
        print()
    
    results = []
    
    # Test Redis
    results.append(("Redis Connection", test_redis_connection()))
    print()
    
    # Test Composio
    results.append(("Composio Connection", test_composio_connection()))
    print()
    
    # Test Composio tools
    results.append(("Composio Tools", test_composio_tools()))
    print()
    
    # Test WebRTC Redis integration
    results.append(("WebRTC Redis Integration", test_webrtc_redis_integration()))
    print()
    
    # Test agent integration
    print("🤖 Testing agent integration (this may take a moment)...")
    try:
        agent_result = asyncio.run(test_agent_integration())
        results.append(("Agent Integration", agent_result))
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        results.append(("Agent Integration", False))
    print()
    
    # Summary
    print("=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integrations working perfectly!")
        print("🚀 Your Sambanova project is ready for the Hackathon!")
    elif passed >= total - 1:
        print("⚠️ Most integrations working - check failed test(s)")
    else:
        print("❌ Multiple integration issues - check configuration")
    
    print("=" * 50)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
