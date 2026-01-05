# Comparing Two Inbound Routes for Extension 2001

## Route Comparison

### Route 1: "Twilio-to-Extension-2001"
- **Order:** 330 (processes later)
- **Context:** public
- **Condition:** `destination_number = ^2001$`
- **Action:** `transfer` to `2001@internal`
- **Destination:** True

### Route 2: "twilio-to-2001" ✅ RECOMMENDED
- **Order:** 100 (processes first)
- **Context:** public
- **Condition:** `destination_number = ^2001$`
- **Action:** `transfer` to `2001 XML default`
- **Destination:** False

## Which One is Correct?

**Route 2 ("twilio-to-2001") is the correct one to keep.** Here's why:

### 1. Transfer Action Syntax ✅

**Route 2 uses:** `2001 XML default`
- This is the **standard FreeSWITCH syntax** for transferring to an extension
- `XML default` means: transfer to extension 2001 in the default XML context
- This works reliably for extension routing

**Route 1 uses:** `2001@internal`
- This tries to transfer to extension 2001 in the "internal" context
- May not work correctly if the call is coming from "public" context
- Less standard syntax

### 2. Processing Order ✅

**Route 2 has Order 100:**
- Processes **first** (lower number = higher priority)
- More efficient - matches and routes immediately

**Route 1 has Order 330:**
- Processes much later
- Unnecessary delay if Route 2 already handles it

### 3. Destination Setting ✅

**Route 2 has Destination: False:**
- Correct for inbound routes that define their own actions
- The route handles the routing itself via the action

**Route 1 has Destination: True:**
- Usually used when the route should pass to a destination object
- Less appropriate here since you're using a transfer action

## Recommendation

**DELETE Route 1 ("Twilio-to-Extension-2001")**  
**KEEP Route 2 ("twilio-to-2001")**

Route 2 is correctly configured and uses the standard FreeSWITCH extension transfer syntax.

## Action Items

1. **Delete Route 1:**
   - Go to: Advanced → Inbound Routes
   - Find "Twilio-to-Extension-2001"
   - Click checkbox → DELETE
   - Confirm

2. **Verify Route 2 is correct:**
   - Route name: `twilio-to-2001`
   - Number: `2001`
   - Context: `public`
   - Order: `100`
   - Enabled: `True`
   - Action: `transfer` to `2001 XML default`

3. **Apply Configuration:**
   - Click SAVE on Route 2 (if you made any changes)
   - Go to: Status → SIP Status
   - Click "Reload XML"

4. **Test the transfer again**

## Why Route 2 is Better

1. ✅ Uses standard FreeSWITCH syntax (`2001 XML default`)
2. ✅ Lower order number (processes first, more efficient)
3. ✅ Correct destination setting (False for action-based routes)
4. ✅ Simpler, cleaner configuration
5. ✅ Follows FusionPBX best practices

