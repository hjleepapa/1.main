# Thread ID Lifecycle and Persistence

## Overview

The `thread_id` in LangGraph is used to maintain conversation context across multiple interactions. In the Convonet WebRTC voice assistant, thread IDs follow a specific pattern and persistence model.

## Thread ID Format

Thread IDs are created using the following format:

```python
thread_id = f"user-{user_id}"
# Example: "user-2481f0e8-4a36-41aa-b667-acdbab9549b8"
```

### When Timestamp Suffix is Added

A timestamp suffix is only added when `reset_thread=True`:

```python
thread_suffix = f"-{int(time.time())}" if reset_thread else ""
thread_id = f"user-{user_id}{thread_suffix}" if user_id else f"flask-thread-1{thread_suffix}"
```

**In WebRTC flow**: `reset_thread=False` (see `convonet/webrtc_voice_server.py:1458`), so **NO timestamp suffix is added**.

This means:
- Same `user_id` = Same `thread_id` across all sessions
- Conversation history accumulates across multiple WebRTC sessions
- No automatic thread reset between sessions

## Thread ID Creation

### When is it Created?

The thread ID is created **on first use** when a message is sent to the agent:

1. User logs into WebRTC voice assistant (`/webrtc/voice-assistant`)
2. User speaks (audio is transcribed)
3. First call to `_run_agent_async()` with that `user_id`
4. LangGraph creates the thread if it doesn't exist
5. Thread persists in memory for subsequent calls

**Code Location**: `convonet/routes.py:975`

```python
thread_id = f"user-{user_id}{thread_suffix}" if user_id else f"flask-thread-1{thread_suffix}"
config = {"configurable": {"thread_id": thread_id}}
```

## Thread Persistence

### Storage Mechanism

The agent graph uses **`InMemorySaver()`** as the checkpointer:

**Code Location**: `convonet/assistant_graph_todo.py:432`

```python
return builder.compile(checkpointer=InMemorySaver())
```

### What This Means

1. **In-Memory Storage**: Conversation state is stored in Python process memory
2. **NOT Persisted to Disk**: No database or file storage
3. **Process Lifetime**: Threads exist as long as the Python process is running
4. **Shared Across Sessions**: Same `user_id` = same thread = shared conversation history

### Thread Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│ User logs into WebRTC voice assistant                        │
│ user_id = "2481f0e8-4a36-41aa-b667-acdbab9549b8"            │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ First message sent to agent                                  │
│ thread_id = "user-2481f0e8-4a36-41aa-b667-acdbab9549b8"     │
│ Thread created in InMemorySaver                             │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Conversation history stored in thread                        │
│ - User messages                                              │
│ - Assistant responses                                         │
│ - Tool calls (calendar events, todos, etc.)                  │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ User logs out and logs back in (same user_id)                │
│ Same thread_id is used                                       │
│ Previous conversation history is still available             │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Thread persists until:                                       │
│ 1. Python process restarts (InMemorySaver cleared)           │
│ 2. reset_thread=True is used (creates new thread)           │
└─────────────────────────────────────────────────────────────┘
```

## Why Same Thread ID Across Multiple Logins?

### Key Point: Thread ID is Based on `user_id`, NOT `session_id`

- **WebRTC Session ID**: Unique per login session (e.g., `"abc123-session-xyz"`)
- **Thread ID**: Based on `user_id` (e.g., `"user-2481f0e8-4a36-41aa-b667-acdbab9549b8"`)

**Code Flow**:

1. User logs in → WebRTC session created with unique `session_id`
2. User speaks → Audio transcribed
3. `process_with_agent()` called with `user_id` from session
4. `_run_agent_async()` creates/uses thread based on `user_id`
5. Thread ID = `f"user-{user_id}"` (same for all sessions with same user)

**Result**: Multiple WebRTC sessions with the same `user_id` share the same conversation thread.

## When is Thread ID Removed/Cleared?

### 1. Python Process Restart

When the Flask/Python application restarts:
- All `InMemorySaver` data is lost
- All threads are cleared
- New threads are created on first use

**Common scenarios**:
- Server deployment/restart
- Application crash
- Manual restart

### 2. Explicit Thread Reset

When `reset_thread=True` is used:

```python
thread_suffix = f"-{int(time.time())}"  # Adds timestamp
thread_id = f"user-{user_id}-{timestamp}"  # New thread ID
```

**Current behavior**: WebRTC flow uses `reset_thread=False`, so threads are **NOT reset** between sessions.

### 3. Manual Thread Deletion (Not Currently Implemented)

There's no automatic cleanup mechanism. Threads persist indefinitely in memory until process restart.

## Implications

### ✅ Benefits

1. **Conversation Continuity**: Users can continue previous conversations
2. **Context Preservation**: Agent remembers past interactions
3. **Activity History**: All calendar events, todos created during previous sessions are accessible

### ⚠️ Considerations

1. **Memory Growth**: Long-running processes accumulate conversation history
2. **No Persistence**: Server restart loses all conversation history
3. **Shared Context**: All sessions for same user share conversation history
4. **No Expiration**: Threads never expire automatically

## Current Implementation Details

### WebRTC Voice Assistant Flow

**File**: `convonet/webrtc_voice_server.py`

```python
# Line 1367-1371: process_with_agent called
agent_response, transfer_marker = asyncio.run(process_with_agent(
    transcribed_text,
    session['user_id'],  # ← Used for thread_id
    session['user_name']
))

# Line 1430-1460: process_with_agent implementation
async def process_with_agent(text: str, user_id: str, user_name: str):
    result = await _run_agent_async(
        prompt=text,
        user_id=user_id,  # ← Used to create thread_id
        user_name=user_name,
        reset_thread=False,  # ← Thread NOT reset
        include_metadata=True
    )
```

### Thread ID Retrieval for Call Center Popup

**File**: `convonet/webrtc_voice_server.py:118-119`

```python
# Generate thread_id from user_id (same format as used in _run_agent_async)
thread_id = f"user-{user_id}" if user_id else None
```

This matches the format used in `_run_agent_async()`, ensuring the popup can retrieve conversation history from the same thread.

## Recommendations

### For Production Use

1. **Consider Persistent Storage**: Replace `InMemorySaver()` with `PostgresSaver()` or `RedisSaver()` for persistence across restarts
2. **Thread Expiration**: Implement automatic cleanup of old threads
3. **Session vs Thread**: Consider using session-specific threads if you want separate conversations per login
4. **Thread Reset Option**: Add UI option to start fresh conversation (`reset_thread=True`)

### Current Behavior Summary

- ✅ Thread ID persists across multiple WebRTC logins (same user_id)
- ✅ Conversation history accumulates across sessions
- ⚠️ Threads cleared on server restart
- ⚠️ No automatic expiration
- ⚠️ Memory usage grows over time

## Code References

- Thread ID creation: `convonet/routes.py:975`
- InMemorySaver usage: `convonet/assistant_graph_todo.py:432`
- WebRTC agent processing: `convonet/webrtc_voice_server.py:1367-1460`
- Thread ID retrieval for popup: `convonet/webrtc_voice_server.py:118-119`

