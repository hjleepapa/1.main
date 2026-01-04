"""
LLM Response Viewer Routes for Convonet Project
Dashboard to view and troubleshoot LLM responses, conversation logs, and LangGraph agent interactions
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from flask import Blueprint, render_template, request, jsonify
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

# Apply nest_asyncio to allow nested event loops (needed for eventlet compatibility)
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass  # nest_asyncio not available, may cause issues with eventlet

# Import agent graph and state
try:
    from convonet.routes import _get_agent_graph
    from convonet.state import AgentState
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Agent not available: {e}")
    AGENT_AVAILABLE = False
    _get_agent_graph = None

# Redis for tracking active threads
try:
    from convonet.redis_manager import redis_manager
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis_manager = None

# Create blueprint
llm_viewer_bp = Blueprint('llm_viewer', __name__, url_prefix='/llm-viewer')


def serialize_message(msg) -> Dict[str, Any]:
    """Serialize a LangChain message to JSON-serializable dict"""
    msg_dict = {
        "type": type(msg).__name__,
        "content": str(getattr(msg, 'content', '')),
    }
    
    # Add type-specific fields
    if isinstance(msg, HumanMessage):
        msg_dict["role"] = "user"
    elif isinstance(msg, AIMessage):
        msg_dict["role"] = "assistant"
        # Extract tool calls if present
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "name": tc.get("name", ""),
                    "args": tc.get("args", {}),
                    "id": tc.get("id", "")
                }
                for tc in msg.tool_calls
            ]
    elif isinstance(msg, ToolMessage):
        msg_dict["role"] = "tool"
        if hasattr(msg, 'tool_call_id'):
            msg_dict["tool_call_id"] = msg.tool_call_id
        if hasattr(msg, 'name'):
            msg_dict["tool_name"] = msg.name
    elif isinstance(msg, SystemMessage):
        msg_dict["role"] = "system"
    
    # Add additional metadata if available
    if hasattr(msg, 'additional_kwargs'):
        msg_dict["additional_kwargs"] = msg.additional_kwargs
    
    return msg_dict


def get_conversation_summary(state_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Extract summary information from conversation state"""
    messages = state_dict.get("messages", [])
    
    user_messages = [m for m in messages if isinstance(m, HumanMessage)]
    ai_messages = [m for m in messages if isinstance(m, AIMessage)]
    tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
    
    return {
        "total_messages": len(messages),
        "user_messages": len(user_messages),
        "ai_messages": len(ai_messages),
        "tool_calls": len(tool_messages),
        "last_user_input": str(user_messages[-1].content) if user_messages else None,
        "last_ai_response": str(ai_messages[-1].content) if ai_messages else None,
    }


@llm_viewer_bp.route('/')
def index():
    """Main LLM response viewer dashboard page"""
    return render_template('llm_response_viewer_dashboard.html')


@llm_viewer_bp.route('/api/threads', methods=['GET'])
def api_threads():
    """Get list of available conversation threads"""
    if not AGENT_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'Agent not available',
            'threads': []
        })
    
    try:
        # Run async function in sync context
        agent_graph = asyncio.run(_get_agent_graph())
        
        # Note: InMemorySaver doesn't provide list_threads()
        # We'll need to track threads ourselves or return empty list
        # For now, return empty list with note that threads must be accessed by ID
        
        # If Redis is available, try to get tracked threads
        threads = []
        if REDIS_AVAILABLE and redis_manager and redis_manager.is_available():
            try:
                # Try to get thread IDs from Redis (if we're tracking them)
                thread_keys = redis_manager.redis_client.keys("llm_thread:*")
                for key in thread_keys[:50]:  # Limit to 50 most recent
                    thread_id = key.replace("llm_thread:", "")
                    thread_meta = redis_manager.redis_client.get(key)
                    if thread_meta:
                        meta = json.loads(thread_meta)
                        threads.append({
                            "thread_id": thread_id,
                            "user_id": meta.get("user_id"),
                            "user_name": meta.get("user_name"),
                            "created_at": meta.get("created_at"),
                            "last_updated": meta.get("last_updated"),
                            "message_count": meta.get("message_count", 0)
                        })
            except Exception as e:
                print(f"⚠️ Error reading threads from Redis: {e}")
        
        return jsonify({
            'success': True,
            'threads': threads,
            'note': 'Threads are tracked in-memory. Use /api/conversation/<thread_id> to view specific conversations.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'threads': []
        })


@llm_viewer_bp.route('/api/conversation/<thread_id>', methods=['GET'])
def api_conversation(thread_id: str):
    """Get full conversation for a specific thread"""
    if not AGENT_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'Agent not available'
        })
    
    try:
        agent_graph = asyncio.run(_get_agent_graph())
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get the conversation state
        state = agent_graph.get_state(config=config)
        
        if not state or not state.values:
            return jsonify({
                'success': False,
                'message': f'Conversation thread "{thread_id}" not found'
            })
        
        # Extract state values
        state_dict = state.values
        messages = state_dict.get("messages", [])
        
        # Serialize messages
        serialized_messages = [serialize_message(msg) for msg in messages]
        
        # Get summary
        summary = get_conversation_summary(state_dict)
        
        # Get metadata
        metadata = {
            "thread_id": thread_id,
            "user_id": state_dict.get("authenticated_user_id"),
            "user_name": state_dict.get("authenticated_user_name"),
            "is_authenticated": state_dict.get("is_authenticated", False),
            "customer_id": state_dict.get("customer_id", ""),
            "next": state.next if hasattr(state, 'next') else [],
            "parent": state.parents if hasattr(state, 'parents') else [],
        }
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'metadata': metadata,
            'summary': summary,
            'messages': serialized_messages,
            'message_count': len(serialized_messages)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error retrieving conversation: {str(e)}'
        })


@llm_viewer_bp.route('/api/search', methods=['POST'])
def api_search():
    """Search conversations by thread ID or user ID"""
    if not AGENT_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'Agent not available',
            'results': []
        })
    
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'Query parameter required',
                'results': []
            })
        
        # Try to get conversation with the query as thread_id
        agent_graph = asyncio.run(_get_agent_graph())
        config = {"configurable": {"thread_id": query}}
        
        try:
            state = agent_graph.get_state(config=config)
            if state and state.values:
                messages = state.values.get("messages", [])
                if messages:
                    return jsonify({
                        'success': True,
                        'results': [{
                            'thread_id': query,
                            'found': True,
                            'message_count': len(messages)
                        }]
                    })
        except:
            pass
        
        # If not found, search in Redis tracked threads
        results = []
        if REDIS_AVAILABLE and redis_manager and redis_manager.is_available():
            try:
                thread_keys = redis_manager.redis_client.keys("llm_thread:*")
                for key in thread_keys:
                    if query.lower() in key.lower():
                        thread_id = key.replace("llm_thread:", "")
                        results.append({
                            'thread_id': thread_id,
                            'found': False,  # We know it exists but haven't loaded it
                        })
            except:
                pass
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error searching: {str(e)}',
            'results': []
        })


@llm_viewer_bp.route('/api/analyze/<thread_id>', methods=['GET'])
def api_analyze(thread_id: str):
    """Analyze conversation for debugging insights"""
    if not AGENT_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'Agent not available'
        })
    
    try:
        agent_graph = asyncio.run(_get_agent_graph())
        config = {"configurable": {"thread_id": thread_id}}
        
        state = agent_graph.get_state(config=config)
        if not state or not state.values:
            return jsonify({
                'success': False,
                'message': f'Conversation thread "{thread_id}" not found'
            })
        
        messages = state.values.get("messages", [])
        
        # Analyze conversation
        analysis = {
            "thread_id": thread_id,
            "total_turns": len([m for m in messages if isinstance(m, HumanMessage)]),
            "tool_calls": [],
            "errors": [],
            "patterns": {
                "has_transfer_intent": False,
                "has_tool_calls": False,
                "has_multiple_tool_rounds": False,
            }
        }
        
        tool_call_count = 0
        for msg in messages:
            if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                analysis["patterns"]["has_tool_calls"] = True
                tool_call_count += len(msg.tool_calls)
                for tc in msg.tool_calls:
                    analysis["tool_calls"].append({
                        "name": tc.get("name", "unknown"),
                        "args": tc.get("args", {}),
                    })
            
            if isinstance(msg, ToolMessage):
                content_str = str(msg.content)
                if "ERROR" in content_str.upper() or "FAIL" in content_str.upper():
                    analysis["errors"].append({
                        "tool": getattr(msg, 'name', 'unknown'),
                        "content": content_str[:200]
                    })
            
            if isinstance(msg, (HumanMessage, AIMessage)):
                content_str = str(msg.content)
                if "TRANSFER" in content_str.upper():
                    analysis["patterns"]["has_transfer_intent"] = True
        
        analysis["patterns"]["has_multiple_tool_rounds"] = tool_call_count > 1
        analysis["total_tool_calls"] = tool_call_count
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error analyzing conversation: {str(e)}'
        })

