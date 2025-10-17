# Sentry Integration for Sambanova Voice AI

## Why Sentry for Your Hackathon Project

✅ **5-minute setup** - Add error monitoring instantly  
✅ **Impressive demo** - Show real-time error dashboard  
✅ **Solves real problems** - Track timeout/MCP errors you're experiencing  
✅ **Production-ready** - Actually useful beyond hackathon  

---

## Quick Setup (5 Minutes)

### Step 1: Install Sentry SDK

```bash
cd "/Users/hj/Web Development Projects/1. Main"
pip install sentry-sdk[flask]

# Update requirements.txt
echo "sentry-sdk[flask]" >> requirements.txt
```

### Step 2: Get Sentry DSN

```
1. Go to https://sentry.io (free tier available)
2. Create account / login
3. Create new project → Python/Flask
4. Copy your DSN (looks like: https://xxx@xxx.ingest.sentry.io/xxx)
```

### Step 3: Add to app.py

Edit `/Users/hj/Web Development Projects/1. Main/app.py`:

```python
# Add at the very top, before any other imports
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN', ''),  # From environment variable
    integrations=[
        FlaskIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=1.0,  # 100% of transactions for demo
    profiles_sample_rate=1.0,  # 100% profiling
    environment="production" if os.getenv('RENDER') else "development",
    release=os.getenv('RENDER_GIT_COMMIT', 'dev'),
)

# Rest of your app.py code...
```

### Step 4: Add DSN to .env

```bash
# Add to .env
SENTRY_DSN=https://your-sentry-dsn@ingest.sentry.io/project-id
```

### Step 5: Deploy to Render

```bash
git add app.py requirements.txt
git commit -m "Add Sentry error monitoring"
git push origin main
```

Add environment variable in Render:
```
Render Dashboard → Your Service → Environment
SENTRY_DSN = https://your-sentry-dsn...
```

---

## What Sentry Will Track

### Automatically Captured:

1. **All Python Exceptions**
   - BrokenResourceError
   - Timeout errors
   - tool_call_id errors
   - Database errors

2. **HTTP Requests**
   - Twilio webhooks
   - Response times
   - Status codes

3. **Performance**
   - Slow tool executions (>8s)
   - Database query times
   - API call durations

4. **Context**
   - User ID
   - Call SID
   - Request parameters
   - Stack traces

---

## Custom Event Tracking (Optional)

### Track Tool Performance

```python
# In assistant_graph_todo.py
import sentry_sdk

# Before tool execution
with sentry_sdk.start_transaction(op="tool", name=tool_name):
    result = await tool.ainvoke(tool_args)
    
# Sentry will track duration automatically
```

### Track Voice Call Events

```python
# In routes.py
@sambanova_todo_bp.route('/twilio/process_audio', methods=['POST'])
def process_audio_webhook():
    call_sid = request.form.get('CallSid')
    
    # Set context for this call
    sentry_sdk.set_context("call", {
        "call_sid": call_sid,
        "user_id": request.args.get('user_id'),
        "transcribed_text": request.form.get('SpeechResult')
    })
    
    # Your existing code...
```

### Track Timeouts

```python
# In routes.py - when timeout occurs
except asyncio.TimeoutError:
    sentry_sdk.capture_message(
        f"Agent timeout for user {user_id}",
        level="warning",
        extras={"prompt": transcribed_text}
    )
    # Your existing code...
```

---

## Hackathon Demo Value

### Before Demo:
```
Judges: "How do you handle errors?"
You: "Uh, we log them to console..."
```

### After Adding Sentry:
```
Judges: "How do you handle errors?"
You: "We use Sentry for real-time error monitoring!"
[Show dashboard with:]
- Error rate graphs
- Performance metrics
- User session replays
- Alert notifications
```

**Impact:** 🚀 Professional, production-grade monitoring

---

## Dashboard Features You Can Show

1. **Error Dashboard**
   - Real-time error count
   - Error types breakdown
   - Affected users

2. **Performance Monitoring**
   - Tool execution times
   - Slowest operations
   - Timeout rates

3. **User Sessions**
   - Complete conversation flow
   - Where users get stuck
   - Success/failure rates

4. **Alerts**
   - Slack/email when errors spike
   - Custom alerts for tool failures

---

## Cost

- **Free tier:** 5,000 errors/month
- **Perfect for hackathon** and small production
- No credit card needed to start

---

## Alternative: Redpanda for Real-Time Analytics

If you want to impress with real-time features:

### Quick Integration

```python
# Install
pip install kafka-python

# In routes.py
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=os.getenv('REDPANDA_BROKER', 'localhost:9092'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Publish events
@sambanova_todo_bp.route('/twilio/process_audio', methods=['POST'])
def process_audio_webhook():
    # Publish event
    producer.send('voice-calls', {
        'event': 'tool_executed',
        'tool': 'create_todo',
        'user_id': user_id,
        'timestamp': time.time()
    })
```

### Then Build Dashboard

```python
# Consumer reads events and updates real-time analytics
# Show live metrics during demo:
# - Calls per minute
# - Tools usage distribution
# - Average response time
```

---

## 🎯 My Recommendation

### For Maximum Hackathon Impact:

**Option 1: Sentry Only** (If time is limited)
- ⏱️ Setup: 5 minutes
- 💪 Impact: High
- 🎯 Demonstrates: Production-grade engineering

**Option 2: Sentry + Redpanda** (If you have 1-2 days)
- ⏱️ Setup: 2-3 hours
- 💪 Impact: Very High
- 🎯 Demonstrates: Real-time architecture + monitoring

**Skip:**
- TrueFoundry (you're not deploying custom models)
- StackAI (duplicates your LangGraph)
- Others (unknown/unclear value add)

---

## Next Steps

Would you like me to:
1. ✅ Create Sentry integration code?
2. ✅ Create Redpanda event streaming setup?
3. ✅ Both?

Let me know which direction you want to go for the hackathon!

