# Call Center: Two Pop-ups Issue

## Problem Description

When a call is transferred from the voice assistant to the agent desktop, two customer information pop-ups appear instead of one.

## Root Cause Analysis

The two pop-ups appear due to the call transfer flow involving multiple SIP INVITEs:

### Call Transfer Flow

1. **First INVITE (Parent Call)**: 
   - Twilio initiates a call to the agent extension (2001)
   - This is the initial call leg from Twilio
   - Call-ID: `3b750439-64c9-123f-82a8-42010a80000a`
   - When this INVITE arrives, the agent's desktop client:
     - Detects incoming call
     - Shows customer popup #1
     - Enables Answer button

2. **Second INVITE (Dial Leg)**:
   - Twilio sends a second INVITE (Dial leg) to establish the actual connection
   - This is the "Dial leg" that connects the user to the agent
   - Call-ID: `3d9c5912-64c9-123f-82a8-42010a80000a` (different Call-ID)
   - Arrives ~3-4 seconds after the first INVITE
   - When this INVITE arrives, the agent's desktop client:
     - Detects it as a Dial leg (different Call-ID, within time window)
     - Shows customer popup #2
     - Auto-answers the call

### Why Two Pop-ups?

The customer popup is triggered in two places:

1. **First Popup**: Triggered when `handleIncomingCall()` processes the first INVITE
   - Location: `call_center.js:584` - `handleIncomingCall()`
   - Calls `showCustomerPopup(customerId)` at line 633
   - This happens for the parent call

2. **Second Popup**: Triggered when `handleParallelInviteDuringActiveCall()` detects the Dial leg
   - Location: `call_center.js:797` - `handleParallelInviteDuringActiveCall()`
   - Calls `showCustomerPopup(customerId)` at line 871
   - This happens when switching to the Dial leg session

### Code Flow

```
First INVITE arrives
  ↓
handleIncomingCall(session)
  ↓
showCustomerPopup(customerId)  ← POPUP #1
  ↓
Dial leg INVITE arrives (~3-4 seconds later)
  ↓
handleParallelInviteDuringActiveCall(session)
  ↓
showCustomerPopup(customerId)  ← POPUP #2
```

## Current Behavior

- Both pop-ups display the same customer information
- Both have "Accept Call" buttons
- The first popup appears, then the second popup appears on top
- The call is successfully connected (auto-answered on Dial leg)

## Impact

- **User Experience**: Confusing to see two identical pop-ups
- **Functionality**: No functional impact - call still connects successfully
- **Priority**: Low - cosmetic issue, can be fixed later

## Proposed Solutions (Future Fixes)

### Option 1: Suppress Popup for Parent Call
- Only show popup when Dial leg is detected
- Skip popup for the first INVITE if we expect a Dial leg

### Option 2: Close First Popup When Dial Leg Arrives
- When Dial leg is detected, close the first popup before showing the second
- Ensure smooth transition

### Option 3: Track Popup State
- Add a flag to track if popup is already shown
- Only show popup if not already visible

### Option 4: Delay First Popup
- Wait a short time (e.g., 5 seconds) before showing popup
- If Dial leg arrives within that time, only show one popup

## Recommended Solution

**Option 2** is recommended because:
- It's the cleanest user experience
- Ensures only one popup is visible at a time
- Maintains all existing functionality
- Easy to implement

## Implementation Notes

The fix should be in `call_center.js`:
- In `handleIncomingCall()`, check if we're expecting a Dial leg
- In `handleParallelInviteDuringActiveCall()`, close existing popup before showing new one
- Use `hideCustomerPopup()` before `showCustomerPopup()` when switching to Dial leg

## Related Code Locations

- `call_center/static/js/call_center.js`:
  - Line 584: `handleIncomingCall()` - shows first popup
  - Line 797: `handleParallelInviteDuringActiveCall()` - shows second popup
  - Line 633: First `showCustomerPopup()` call
  - Line 871: Second `showCustomerPopup()` call

## Status

- **Current**: Issue documented, low priority
- **Future**: Will be fixed when time permits
- **Workaround**: User can close the first popup manually

