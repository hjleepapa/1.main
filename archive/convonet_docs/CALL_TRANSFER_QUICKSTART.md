# Call Transfer Quick Start

## Setup (5 minutes)

### 1. Add Environment Variable
```bash
# Add to your .env file
FREEPBX_DOMAIN=34.26.59.14
```

### 2. Configure Extensions
Edit `convonet/mcps/local_servers/call_transfer.py`:
```python
EXTENSION_MAP = {
    'support': '2000',  # Your support queue/extension
    'sales': '2000',    # Your sales queue/extension
    'general': '2000',  # Your general queue/extension
    'operator': '2000', # Your operator
}
```

### 3. Restart Application
```bash
# The transfer tools are automatically loaded
# No additional configuration needed!
```

## Usage

### As a Caller
Simply say any of these phrases during your call:
- "Transfer me to an agent"
- "I need to speak with someone"
- "Connect me to support"
- "Talk to a human"
- "Speak to a real person"

### Automatic Transfer
The AI will automatically transfer if it detects:
- User frustration
- Complex requests beyond AI capability
- User explicitly requesting human assistance

## How Transfer Works

```
User says "transfer me"
    ↓
LangGraph detects intent
    ↓
Calls transfer_to_agent() tool
    ↓
Returns TRANSFER_INITIATED marker
    ↓
Webhook redirects to /twilio/transfer
    ↓
Twilio generates <Dial> TwiML
    ↓
Call connects to FreePBX extension
```

## Test Your Setup

### Test 1: Direct Transfer Endpoint
```bash
curl -X POST https://hjlees.com/convonet_todo/twilio/transfer \
  -d "extension=2000"
```

Expected: Returns TwiML with `<Dial>sip:201@34.26.59.14</Dial>`

### Test 2: Voice Call
1. Call your Twilio number
2. Enter PIN
3. Say: "Transfer me to support"
4. Should hear: "Transferring you to an agent. Please wait."
5. Call connects to FreePBX extension 2000

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Transfer drops call | Check FreePBX extension is online and answering |
| AI doesn't transfer | Verify `FREEPBX_DOMAIN` is set correctly |
| Wrong extension | Update `EXTENSION_MAP` in `call_transfer.py` |
| No audio after transfer | Check SIP trunk between Twilio and FreePBX |

## Advanced Configuration

### Custom Routing by Time
```python
# In call_transfer.py
def get_extension_by_schedule():
    hour = datetime.now().hour
    if 9 <= hour < 17:
        return "201"  # Business hours
    return "200"     # After hours
```

### Priority Routing
```python
# Transfer VIP customers to special queue
if customer_tier == "VIP":
    transfer_to_agent(extension="2000", reason="VIP customer")
```

## Files Modified

✅ `convonet/routes.py` - Added `/twilio/transfer` endpoint and detection logic
✅ `convonet/twilio_handler.py` - Added WebSocket transfer handling  
✅ `convonet/assistant_graph_todo.py` - Updated system prompt with transfer examples
✅ `convonet/mcps/local_servers/call_transfer.py` - New transfer tool module

## Next Steps

1. **Monitor Transfers**: Add logging to track transfer success rate
2. **Customize Messages**: Edit transfer messages in routes.py
3. **Add More Queues**: Extend `EXTENSION_MAP` with your queues
4. **Intelligent Routing**: Use LangGraph to analyze conversation context

## Support

See full documentation: `CALL_TRANSFER_GUIDE.md`

