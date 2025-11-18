#!/usr/bin/env python3
"""
Test Script: Composio Slack Integration
Quick test to verify Composio Slack tools are working
"""

import os
import sys
import asyncio

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from convonet.composio_tools import ComposioManager

async def test_composio_slack():
    """Test Composio Slack integration"""
    print("🧪 Testing Composio Slack Integration")
    print("=" * 40)
    
    # Initialize Composio
    composio = ComposioManager()
    
    if not composio.is_available():
        print("❌ Composio not available")
        print("Check COMPOSIO_API_KEY environment variable")
        return False
    
    print("✅ Composio initialized successfully")
    
    # Test Slack tools
    print("\n🔍 Testing Slack tools...")
    slack_tools = composio.get_slack_tools()
    
    if slack_tools:
        print(f"✅ Found {len(slack_tools)} Slack tools")
        for i, tool in enumerate(slack_tools[:3], 1):  # Show first 3 tools
            print(f"  {i}. {tool}")
    else:
        print("❌ No Slack tools found")
        print("Check Slack workspace connection in Composio dashboard")
        return False
    
    # Test available apps
    print("\n🔍 Testing available apps...")
    try:
        apps = composio.get_available_apps()
        if apps:
            print(f"✅ Found {len(apps)} available apps")
            for app in apps[:5]:  # Show first 5 apps
                print(f"  • {app}")
        else:
            print("⚠️ No apps found")
    except Exception as e:
        print(f"⚠️ Error getting apps: {e}")
    
    print("\n✅ Composio Slack integration test completed")
    return True

async def main():
    """Main test function"""
    print("🚀 Starting Composio Slack Test")
    
    # Check environment
    api_key = os.getenv('COMPOSIO_API_KEY')
    if not api_key:
        print("⚠️ COMPOSIO_API_KEY not set")
        print("Using demo API key...")
    
    # Run test
    success = await test_composio_slack()
    
    if success:
        print("\n🎉 Composio Slack integration is ready!")
        print("You can now use voice commands to send todos to Slack")
    else:
        print("\n❌ Composio Slack integration needs configuration")
        print("Please check your Composio dashboard and Slack connection")

if __name__ == "__main__":
    asyncio.run(main())
