#!/usr/bin/env python3
"""
Voice Demo: Slack Todo Integration
Simple demo script to test Slack integration with voice commands
"""

import os
import sys
import asyncio
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_voice_commands():
    """Demo voice commands for Slack integration"""
    print("🎤 VOICE COMMANDS FOR SLACK TODO INTEGRATION")
    print("=" * 50)
    
    print("\n📋 Try these voice commands in the WebRTC Voice Assistant:")
    print("(Access at: https://hjlees.com → WebRTC Voice Assistant)")
    
    print("\n1️⃣ **Create Todo Tasks:**")
    print("   Say: 'Create a todo for grocery shopping with high priority'")
    print("   Say: 'Add a task for team meeting preparation'")
    print("   Say: 'Create a reminder to review the quarterly report'")
    
    print("\n2️⃣ **Send Todos to Slack:**")
    print("   Say: 'Send my recent todos to the team Slack channel'")
    print("   Say: 'Post my todo list to #productivity channel'")
    print("   Say: 'Share my tasks with the team on Slack'")
    
    print("\n3️⃣ **Slack Integration Commands:**")
    print("   Say: 'Show me my todos and send them to Slack'")
    print("   Say: 'Create a todo for code review and notify the team'")
    print("   Say: 'Add a high priority task and post to Slack'")
    
    print("\n🎯 **Expected Demo Flow:**")
    print("1. Voice assistant creates todo tasks")
    print("2. Tasks are stored in database")
    print("3. Composio integration sends formatted message to Slack")
    print("4. Team sees todo list in Slack channel")
    print("5. Activity is tracked in Redis")
    
    print("\n📱 **Slack Channel Setup:**")
    print("1. Create a Slack workspace or use existing")
    print("2. Create a channel like #productivity or #todos")
    print("3. Note the channel name (e.g., #productivity)")
    print("4. Configure Composio with your Slack workspace")
    
    print("\n🔧 **Composio Configuration:**")
    print("1. Go to Composio dashboard")
    print("2. Connect Slack workspace")
    print("3. Authorize the integration")
    print("4. Set environment variables:")
    print("   - COMPOSIO_API_KEY")
    print("   - COMPOSIO_PROJECT_ID")
    
    print("\n✅ **Success Indicators:**")
    print("- Voice assistant confirms todo creation")
    print("- Slack message appears in channel")
    print("- Formatted todo list with priorities")
    print("- Redis activity tracking works")
    print("- No errors in console logs")

def demo_slack_message_format():
    """Show example Slack message format"""
    print("\n📝 **Example Slack Message Format:**")
    print("-" * 40)
    
    sample_message = """📋 *Recent Todo Tasks:*

1. 🔴 *Grocery Shopping*
   📝 Buy milk, bread, and eggs
   ⏳ Status: Pending
   📅 Created: 2025-10-25

2. 🟡 *Team Meeting Prep*
   📝 Prepare presentation for Q4 review
   🔄 Status: In Progress
   📅 Created: 2025-10-25

3. 🟢 *Code Review*
   📝 Review pull request #123
   ⏳ Status: Pending
   📅 Created: 2025-10-25"""
    
    print(sample_message)
    print("-" * 40)

def demo_troubleshooting():
    """Troubleshooting guide"""
    print("\n🔧 **Troubleshooting Guide:**")
    print("=" * 30)
    
    print("\n❌ **Common Issues:**")
    print("1. 'Composio not available'")
    print("   → Check COMPOSIO_API_KEY environment variable")
    print("   → Verify Composio dashboard connection")
    
    print("\n2. 'No Slack tools available'")
    print("   → Ensure Slack workspace is connected in Composio")
    print("   → Check OAuth2 authorization")
    
    print("\n3. 'Message not appearing in Slack'")
    print("   → Verify channel name (e.g., #general)")
    print("   → Check bot permissions in Slack")
    print("   → Ensure bot is added to the channel")
    
    print("\n4. 'Redis connection failed'")
    print("   → Check REDIS_URL environment variable")
    print("   → Verify Redis server is running")
    
    print("\n✅ **Verification Steps:**")
    print("1. Check console logs for Composio initialization")
    print("2. Verify Slack tools are loaded")
    print("3. Test Redis connection")
    print("4. Check Slack channel for messages")

if __name__ == "__main__":
    demo_voice_commands()
    demo_slack_message_format()
    demo_troubleshooting()
    
    print("\n" + "="*60)
    print("🎯 READY FOR DEMO!")
    print("="*60)
    print("Navigate to: https://hjlees.com")
    print("Click: '🌐 WebRTC Voice Assistant'")
    print("Say: 'Send my todos to Slack'")
    print("="*60)
