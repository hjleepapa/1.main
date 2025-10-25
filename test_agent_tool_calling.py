#!/usr/bin/env python3
"""
Test Agent Tool Calling
Test if the agent properly uses tools for specific requests
"""

import os
import sys
import asyncio

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_agent_tool_calling():
    """Test if agent uses tools for specific requests"""
    try:
        from sambanova.assistant_graph_todo import get_agent
        
        print("🤖 Testing Agent Tool Calling...")
        print("=" * 50)
        
        # Get the agent
        agent = get_agent()
        print(f"✅ Agent initialized with {len(agent.tools)} tools")
        
        # Test different types of requests
        test_requests = [
            "Thanks for watching!",  # Should NOT use tools (polite response)
            "Create a todo for grocery shopping",  # Should use create_todo
            "What are my todos?",  # Should use get_todos
            "Send a Slack message to the team",  # Should use Slack tools
            "Create a GitHub issue for the bug",  # Should use GitHub tools
        ]
        
        for request in test_requests:
            print(f"\n🧪 Testing: '{request}'")
            print("-" * 40)
            
            # Create a simple state for testing
            from sambanova.state import AgentState
            from langchain_core.messages import HumanMessage
            
            state = AgentState(
                messages=[HumanMessage(content=request)],
                authenticated_user_id="test_user",
                user_name="Test User"
            )
            
            # Run the assistant node
            try:
                # Get the assistant function from the agent
                assistant_func = None
                for node_name, node_func in agent.graph.nodes.items():
                    if node_name == "assistant":
                        assistant_func = node_func
                        break
                
                if assistant_func:
                    result_state = await assistant_func(state)
                    last_message = result_state.messages[-1]
                    
                    print(f"📝 Response: {last_message.content}")
                    
                    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                        print(f"🔧 Tool calls made: {len(last_message.tool_calls)}")
                        for tool_call in last_message.tool_calls:
                            print(f"  - {tool_call['name']}: {tool_call.get('args', {})}")
                    else:
                        print("❌ No tool calls made")
                        
                else:
                    print("❌ Could not find assistant function")
                    
            except Exception as e:
                print(f"❌ Error testing request: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n✅ Agent tool calling test completed")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_tool_calling())
