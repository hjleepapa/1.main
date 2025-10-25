#!/usr/bin/env python3
"""
Test Voice Commands for Tool Calling
Test specific voice commands that should trigger tool usage
"""

import os
import sys
import asyncio

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_voice_commands():
    """Test voice commands that should trigger tool usage"""
    try:
        from sambanova.assistant_graph_todo import get_agent
        
        print("🎤 Testing Voice Commands for Tool Calling...")
        print("=" * 60)
        
        # Get the agent
        agent = get_agent()
        print(f"✅ Agent initialized with {len(agent.tools)} tools")
        
        # Debug: Check what tools are available
        if len(agent.tools) == 0:
            print("⚠️ No tools loaded - this might be why tool calling isn't working")
            print("🔍 Checking agent configuration...")
            
            # Check if tools are properly bound to LLM
            if hasattr(agent.llm, 'bound') and agent.llm.bound:
                print("✅ LLM has bound tools")
            else:
                print("❌ LLM does not have bound tools")
                
            # Check if tools list is empty
            if not agent.tools:
                print("❌ Agent tools list is empty")
            else:
                print(f"📋 Agent tools: {[tool.name for tool in agent.tools[:5]]}...")
        else:
            print(f"📋 Available tools: {[tool.name for tool in agent.tools[:5]]}...")
        
        # Test commands that SHOULD use tools
        tool_commands = [
            "Create a todo for grocery shopping",
            "What are my todos?",
            "Show me my tasks",
            "Create a reminder to call mom tomorrow",
            "Add a calendar event for the meeting",
        ]
        
        # Test commands that should NOT use tools
        polite_commands = [
            "Thanks for watching!",
            "Hello",
            "Goodbye",
            "How are you?",
        ]
        
        print("\n🔧 Testing Tool-Requiring Commands:")
        print("-" * 50)
        
        for command in tool_commands:
            print(f"\n🧪 Testing: '{command}'")
            await test_single_command(agent, command)
        
        print("\n💬 Testing Polite Commands (No Tools Expected):")
        print("-" * 50)
        
        for command in polite_commands:
            print(f"\n🧪 Testing: '{command}'")
            await test_single_command(agent, command)
        
        print("\n✅ Voice command testing completed")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

async def test_single_command(agent, command):
    """Test a single voice command"""
    try:
        from sambanova.state import AgentState
        from langchain_core.messages import HumanMessage
        
        # Create state for testing
        state = AgentState(
            messages=[HumanMessage(content=command)],
            authenticated_user_id="test_user",
            user_name="Test User"
        )
        
        # Use the agent's graph directly instead of trying to access individual nodes
        try:
            # Run the graph with the input state
            result = agent.graph.invoke(state)
            last_message = result.messages[-1]
            
            print(f"📝 Response: {last_message.content[:100]}...")
            
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                print(f"🔧 ✅ Tool calls made: {len(last_message.tool_calls)}")
                for tool_call in last_message.tool_calls:
                    print(f"  - {tool_call['name']}: {tool_call.get('args', {})}")
            else:
                print("❌ No tool calls made")
                
        except Exception as graph_error:
            print(f"❌ Graph execution error: {graph_error}")
            # Try alternative approach - direct LLM call
            try:
                from langchain_core.messages import SystemMessage
                
                # Create system prompt
                system_prompt = agent.system_prompt.format(
                    todo_priorities="low, medium, high",
                    reminder_importance="low, medium, high"
                )
                
                # Call LLM directly
                response = await agent.llm.ainvoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=command)
                ])
                
                print(f"📝 Direct LLM Response: {response.content[:100]}...")
                
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    print(f"🔧 ✅ Tool calls made: {len(response.tool_calls)}")
                    for tool_call in response.tool_calls:
                        print(f"  - {tool_call['name']}: {tool_call.get('args', {})}")
                else:
                    print("❌ No tool calls made")
                    
            except Exception as llm_error:
                print(f"❌ Direct LLM call error: {llm_error}")
            
    except Exception as e:
        print(f"❌ Error testing command '{command}': {e}")

if __name__ == "__main__":
    asyncio.run(test_voice_commands())
