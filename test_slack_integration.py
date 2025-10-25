#!/usr/bin/env python3
"""
Test Slack Integration with Composio
Shows what Slack tools are available and how they work
"""

import os
import sys
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_slack_tools():
    """Test what Slack tools are available"""
    try:
        from sambanova.composio_tools import ComposioManager
        
        print("🔧 Testing Slack Integration with Composio...")
        print("=" * 60)
        
        # Initialize Composio manager
        manager = ComposioManager()
        
        if not manager.is_available():
            print("❌ Composio not available")
            return
        
        print("✅ Composio client initialized")
        
        # Get Slack tools
        slack_tools = manager.get_slack_tools()
        
        print(f"\n📋 Found {len(slack_tools)} Slack tools:")
        print("-" * 40)
        
        for i, tool in enumerate(slack_tools, 1):
            print(f"{i}. {tool.name}")
            if hasattr(tool, 'description'):
                print(f"   Description: {tool.description}")
            if hasattr(tool, 'parameters'):
                print(f"   Parameters: {tool.parameters}")
            print()
        
        # Test connection
        print("🔗 Testing Composio connection...")
        if manager.test_connection():
            print("✅ Composio connection successful")
        else:
            print("❌ Composio connection failed")
        
        # Get available apps
        print("\n📱 Available Composio apps:")
        apps = manager.get_available_apps()
        for app in apps:
            print(f"  - {app}")
        
        return slack_tools
        
    except Exception as e:
        print(f"❌ Error testing Slack integration: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_specific_slack_tool(tool_name):
    """Test a specific Slack tool"""
    try:
        from sambanova.composio_tools import ComposioManager
        
        manager = ComposioManager()
        if not manager.is_available():
            print("❌ Composio not available")
            return
        
        slack_tools = manager.get_slack_tools()
        
        # Find the specific tool
        target_tool = None
        for tool in slack_tools:
            if tool.name == tool_name:
                target_tool = tool
                break
        
        if not target_tool:
            print(f"❌ Tool '{tool_name}' not found")
            return
        
        print(f"🔧 Testing tool: {target_tool.name}")
        print(f"Description: {getattr(target_tool, 'description', 'No description')}")
        print(f"Parameters: {getattr(target_tool, 'parameters', 'No parameters')}")
        
        # This would be where you'd actually call the tool
        # For now, just show the tool structure
        print(f"✅ Tool '{tool_name}' is available for use")
        
    except Exception as e:
        print(f"❌ Error testing tool '{tool_name}': {e}")

if __name__ == "__main__":
    print("🚀 Slack Integration Test")
    print("=" * 60)
    
    # Test all Slack tools
    slack_tools = test_slack_tools()
    
    if slack_tools:
        print("\n🎯 Available Slack Tools Summary:")
        print("-" * 40)
        for tool in slack_tools:
            print(f"• {tool.name}")
        
        # Test a specific tool if available
        if slack_tools:
            first_tool = slack_tools[0]
            print(f"\n🔧 Testing first tool: {first_tool.name}")
            test_specific_slack_tool(first_tool.name)
    
    print("\n✅ Slack integration test completed")
