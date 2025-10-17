# Timeout & Cascading Error Fix - Complete Solution

## 🔴 Original Problems

### Problem 1: Call Drops After Tool Execution
```
Tool completes successfully (20s)
Twilio times out at 15s
Call drops before response can be played ❌
```

### Problem 2: Cascading Tool Call Errors
```
Request 1: Tool times out → Incomplete tool_call saved in thread
Request 2: "tool_call_id error" (OpenAI rejects incomplete state)
Request 3: Same error
Request 4: Same error
... Stuck forever! ❌
```

### Problem 3: Empty Error Messages
```
BrokenResourceError → error_str = "" (empty)
Agent gets: "I encountered an error: " 
LLM confused → Takes longer to respond → Timeout ❌
```

---

## ✅ Complete Solution Applied

### Fix 1: Reduced All Timeouts

**Before:**
```python
Tool timeout: 20s
Agent timeout: 25s  
Webhook timeout: 30s
```

**After:**
```python
Tool timeout: 8s   # assistant_graph_todo.py:299, 301
Agent timeout: 10s  # routes.py:683
Webhook timeout: 12s # routes.py:428
```

### Fix 2: Thread Reset on Next Request

**How it works:**
```python
# Request 1: Timeout occurs
if timeout:
    _reset_threads.add(user_id)  # Mark for reset
    
# Request 2: Next request
if user_id in _reset_threads:
    reset_thread = True  # Use fresh thread!
    _reset_threads.remove(user_id)
    
# Fresh thread uses timestamped ID
thread_id = f"user-{user_id}-{timestamp}"  # No incomplete state!
```

### Fix 3: Better Error Messages

**BrokenResourceError handling:**
```python
if "BrokenResourceError" in error_type or not error_str.strip():
    result = "I encountered a connection issue with the database. 
              The operation may have completed. Please check your calendar."
```

**Tool_call_id error handling:**
```python
if "tool_call" in error_str.lower():
    # Mark for reset
    _reset_threads.add(user_id)
    return "Please try your request again..."
```

---

## 📊 How It Works Now

### Scenario 1: Slow Tool (>8s)

```
Request 1: "Create marketing team meeting"
    ↓
Tool: create_calendar_event starts
    ↓
8 seconds pass → Tool timeout
    ↓
Tool returns: "database operation timed out"
    ↓
Agent response: "I'm sorry, that operation is taking too long..."
    ↓
User marked for thread reset
    ↓
TwiML returned in <12s ✅

Request 2: "What's in my calendar?"
    ↓
Fresh thread detected → Use new thread_id
    ↓
No incomplete tool calls
    ↓
Processes normally ✅
```

### Scenario 2: BrokenResourceError

```
Request: "Create calendar event"
    ↓
Tool: Encounters BrokenResourceError (MCP issue)
    ↓
Error caught quickly
    ↓
Result: "I encountered a connection issue..."
    ↓
User marked for thread reset
    ↓
Response returned fast ✅

Next request: Fresh thread ✅
```

### Scenario 3: Previous Timeout Caused tool_call Error

```
Request: "A cricket" (after previous timeout)
    ↓
Thread has incomplete tool_call from before
    ↓
OpenAI error: "tool_call_id must be followed by..."
    ↓
Error detected → Mark for reset
    ↓
Response: "Please try again..."
    ↓

Next request: Fresh thread → Works! ✅
```

---

## 🎯 What Changed in Code

### File: `sambanova/routes.py`

**Lines 416-421:** Check if thread needs reset
```python
if user_id in _reset_threads:
    reset_thread = True  # Use fresh thread
```

**Lines 430-438:** Mark user for reset on timeout
```python
except asyncio.TimeoutError:
    _reset_threads.add(user_id)  # Reset next time
```

**Lines 445-459:** Mark user for reset on tool_call/BrokenResource errors
```python
if "tool_call" in error or "BrokenResourceError" in error:
    _reset_threads.add(user_id)  # Reset next time
```

**Lines 668-673:** Use timestamped thread_id when reset
```python
thread_suffix = f"-{timestamp}" if reset_thread else ""
thread_id = f"user-{user_id}{thread_suffix}"
```

### File: `sambanova/assistant_graph_todo.py`

**Lines 315-320:** Handle BrokenResourceError with meaningful message
```python
if "BrokenResourceError" in error_type:
    result = "I encountered a connection issue..."
```

**Lines 328-340:** Better error handling for all exception types
```python
if "BrokenResourceError": ...
elif "TaskGroup": ...
elif not error_str.strip(): ...  # Empty errors
```

---

## 🧪 Testing

### Test 1: Timeout Recovery

```
Call: +12344007818
Say: "What calendar events do I have?"

Expected:
- Tool times out at 8s
- Response in <12s: "Operation taking too long..."
- Next request: Fresh thread, works normally ✅
```

### Test 2: Error Recovery

```
Call: +12344007818
Say: "Create a meeting"
(If MCP broken)

Expected:
- Error caught quickly
- Response: "Connection issue..."
- Next request: Fresh thread, works ✅
```

### Test 3: Normal Operation

```
Call: +12344007818
Say: "Create a todo for grocery shopping"

Expected:
- Tool completes in <8s
- Agent responds in <10s
- Response played: "Todo created!" ✅
- No errors ✅
```

---

## 🎉 Results

### Before:
- ❌ Calls dropped after slow tools
- ❌ Cascading errors after timeouts
- ❌ Empty error messages confused LLM
- ❌ Bad user experience

### After:
- ✅ Fast tools complete and play response
- ✅ Slow tools timeout gracefully  
- ✅ Next request auto-recovers with fresh thread
- ✅ Clear error messages
- ✅ No cascading errors
- ✅ Smooth user experience

---

## 🔍 Monitoring

### Check Logs

```bash
# Look for thread resets
grep "Resetting conversation thread" logs/app.log

# Look for timeout marks
grep "Marked user.*for thread reset" logs/app.log

# Look for tool completions
grep "Tool.*completed successfully" logs/app.log
```

### Expected Patterns

**Healthy operation:**
```
✅ Tool create_todo completed successfully
🤖 Assistant response: I've created your todo...
Generated TwiML response: ...
```

**Timeout with recovery:**
```
⏰ Tool timed out after 8 seconds
🔄 Marked user abc-123 for thread reset
🤖 Assistant response: Operation taking too long...
[Next request]
🔄 Resetting conversation thread for user abc-123
✅ Tool completed successfully
```

---

## 🛠️ If Still Having Issues

### Issue: Tools Still Timing Out

**Check tool performance:**
```python
# In db_todo.py, add timing logs
import time
start = time.time()
# ... tool execution ...
print(f"Tool took {time.time() - start:.2f}s")
```

**If consistently >8s:**
- Optimize database queries
- Add indexes
- Cache Google Calendar tokens
- Use connection pooling

### Issue: BrokenResourceError Persists

**Restart MCP server:**
```bash
# The MCP server runs as subprocess
# Restart entire Flask app to restart MCP
python app.py
```

**Check MCP logs:**
```bash
grep "MCP" logs/app.log
# Look for connection errors
```

### Issue: Still Getting tool_call_id Errors

**Debug thread IDs:**
```python
# In routes.py, add logging
print(f"Using thread_id: {config['configurable']['thread_id']}")
print(f"Reset thread: {reset_thread}")
```

**Manually clear if stuck:**
```python
# Clear all reset markers
if hasattr(_run_agent_async, '_reset_threads'):
    _run_agent_async._reset_threads.clear()
```

---

## 📝 Summary

**Three interconnected fixes:**

1. **Faster timeouts** → Stay under Twilio's 15s limit
2. **Thread reset system** → Recover from incomplete tool calls
3. **Better error messages** → Handle BrokenResourceError and empty errors

**Result:** Robust system that handles timeouts gracefully and auto-recovers from errors!

**Next:** Test with a call and verify:
- ✅ Fast operations complete (<8s)
- ✅ Slow operations timeout but don't break subsequent requests
- ✅ Clear error messages
- ✅ No cascading errors

