# Call Transfer Guide

## Overview
This guide explains how to use the call transfer feature to transfer calls from the LangGraph voice AI to FreePBX call center agents or queues.

## Architecture

The call transfer system has three main components:

1. **Transfer Tool** (`call_transfer.py`): LangGraph tool that detects transfer requests
2. **Transfer Endpoint** (`/twilio/transfer`): Twilio webhook that generates TwiML for call transfer
3. **Transfer Detection**: Logic in both TwiML and WebSocket flows to detect and handle transfers

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# FreePBX Configuration
FREEPBX_DOMAIN=34.26.59.14  # Your FreePBX server IP or domain
```

### FreePBX Extension Mapping

Edit `convonet/mcps/local_servers/call_transfer.py` to configure your extensions:

```python
EXTENSION_MAP = {
    'support': '2000',  # Support queue
    'sales': '2000',    # Sales queue
    'general': '2000',  # General queue
    'operator': '2000', # Main operator
}
```

## How It Works

### Flow 1: TwiML-based Transfer (HTTP/POST)

1. User says a transfer phrase (e.g., "transfer me", "speak to agent")
2. `process_audio_webhook()` detects the phrase
3. Redirects to `/twilio/transfer?extension=201`
4. Transfer endpoint generates TwiML with `<Dial>` verb
5. Twilio connects the call to FreePBX

### Flow 2: Agent-initiated Transfer (LangGraph Tool)

1. User says "I need help" or similar
2. LangGraph agent calls `transfer_to_agent()` tool
3. Tool returns `TRANSFER_INITIATED:201|support|reason`
4. Webhook detects marker and redirects to transfer endpoint
5. Call is transferred to FreePBX

### Flow 3: WebSocket-based Transfer

1. User says transfer request during WebSocket stream
2. LangGraph agent calls `transfer_to_agent()` tool
3. `twilio_handler.py` detects `TRANSFER_INITIATED` marker
4. Sends Twilio Media Stream `mark` event with transfer parameters
5. Application can handle the mark event to redirect call

## Usage Examples

### User Requests

The AI will automatically detect these phrases and initiate transfer:

- "Transfer me to an agent"
- "I need to speak with someone"
- "Connect me to support"
- "Talk to a real person"
- "I need help from a human"

### Programmatic Transfer

Use the LangGraph tool directly:

```python
from convonet.mcps.local_servers.call_transfer import transfer_to_agent

# Transfer to support queue
result = transfer_to_agent(
    department="support",
    reason="User needs technical assistance"
)

# Transfer to specific extension
result = transfer_to_agent(
    extension="205",
    reason="User requested manager"
)
```

## Testing

### Test Transfer Endpoint

```bash
curl -X POST https://hjlees.com/convonet_todo/twilio/transfer \
  -d "extension=201" \
  -d "CallSid=test123"
```

### Test via Voice Call

1. Call your Twilio number
2. Complete PIN authentication
3. Say: "Transfer me to support"
4. Call should transfer to FreePBX extension 201

## Troubleshooting

### Transfer Not Working

1. **Check FreePBX connectivity**: Ensure Twilio can reach your FreePBX server
   ```bash
   ping 34.26.59.14
   ```

2. **Verify SIP configuration**: Check that Twilio has SIP connectivity to FreePBX
   - Twilio Console → Elastic SIP Trunking
   - Add FreePBX domain to allowed origins

3. **Check logs**:
   ```python
   # In routes.py or twilio_handler.py
   logger.info(f"Transfer request: {extension}")
   ```

4. **Test FreePBX extension directly**: Call the extension from another phone

### Transfer Drops Call

- **Cause**: FreePBX not answering or rejecting the call
- **Solution**: 
  - Check FreePBX extension status
  - Verify SIP trunk configuration
  - Check FreePBX logs: `/var/log/asterisk/full`

### Agent Doesn't Detect Transfer Request

- **Cause**: Transfer tool not loaded or system prompt missing
- **Solution**: 
  - Verify transfer tools are added in `routes.py` and `twilio_handler.py`
  - Check system prompt in `assistant_graph_todo.py`
  - Restart the application

## FreePBX Configuration

### SIP Trunk Setup

1. Log into FreePBX admin panel
2. Go to **Connectivity → Trunks**
3. Add SIP Trunk for Twilio:
   ```
   Trunk Name: Twilio
   Outbound CallerID: Your Twilio Number
   SIP Server: sip.twilio.com
   ```

### Queue Configuration

1. Go to **Applications → Queues**
2. Create or edit queue:
   ```
   Queue Number: 201
   Queue Name: Support Queue
   Static Agents: Add agents
   Ring Strategy: ringall
   ```

### Extension Configuration

1. Go to **Applications → Extensions**
2. Create extension:
   ```
   Extension Number: 201
   Display Name: Support Agent
   ```

## Security Considerations

1. **Firewall**: Ensure FreePBX firewall allows Twilio IPs
2. **Authentication**: FreePBX should authenticate Twilio SIP trunk
3. **Rate Limiting**: Implement rate limiting on transfer endpoint
4. **Logging**: Log all transfer attempts for audit

## Advanced Features

### Custom Transfer Logic

Edit `call_transfer.py` to add custom routing:

```python
def get_department_by_time():
    """Route to different departments based on time of day"""
    from datetime import datetime
    hour = datetime.now().hour
    
    if 9 <= hour < 17:
        return "support"  # Business hours
    else:
        return "operator"  # After hours
```

### Intelligent Routing

Use LangGraph to analyze conversation and route appropriately:

```python
# In system prompt
"If user mentions billing, route to sales department"
"If user mentions technical issue, route to support"
"If user is frustrated (multiple retries), route to supervisor"
```

## Monitoring

Track transfer metrics:

```python
# Add to transfer endpoint
from convonet.mcps.local_servers.db_todo import log_call_transfer

await log_call_transfer(
    call_sid=call_sid,
    from_extension="ai_assistant",
    to_extension=extension,
    transfer_time=datetime.now(),
    reason=reason
)
```

## References

- [Twilio TwiML <Dial> Verb](https://www.twilio.com/docs/voice/twiml/dial)
- [FreePBX Documentation](https://www.freepbx.org/documentation/)
- [LangGraph Tools](https://langchain-ai.github.io/langgraph/concepts/tools/)

