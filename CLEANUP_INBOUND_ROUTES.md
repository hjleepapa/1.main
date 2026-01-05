# Cleanup Multiple Inbound Routes for Extension 2001

## Problem
You have multiple inbound routes configured for routing Twilio calls to extension 2001, which can cause routing conflicts and confusion.

## Solution: Consolidate to One Route

You should have **only ONE inbound route** for routing Twilio calls to extension 2001.

## Step-by-Step Cleanup

### Step 1: Identify Which Route to Keep

Based on your screenshot, you should keep the route with:
- **Name:** `twilio-to-2001` (or choose a clear, descriptive name)
- **Number:** `2001`
- **Context:** `public`
- **Order:** `100` (lower order = processed first)
- **Enabled:** `True`
- **Description:** `Twilio to human agent` (or similar)

**Delete all other duplicate routes** that serve the same purpose.

### Step 2: Delete Duplicate Routes

1. **Login to FusionPBX:** https://136.115.41.45
2. **Navigate:** Advanced → Inbound Routes
3. **For each duplicate route:**
   - Click the checkbox next to the route name
   - Click the **DELETE** button
   - Confirm deletion

**Routes to delete:**
- Any route with name `2001` (duplicate)
- Any route with name `Twilio-to-Extension-2001` (duplicates)
- Keep only ONE route (preferably `twilio-to-2001`)

### Step 3: Verify the Remaining Route Configuration

After deleting duplicates, verify your single route is configured correctly:

**Correct Configuration:**
- **Name:** `twilio-to-2001`
- **Number:** `2001`
- **Context:** `public`
- **Order:** `100` (or any number, but should be lower than catch-all routes like `not-found` which has order 999)
- **Enabled:** `True`
- **Description:** `Twilio to human agent`

### Step 4: Check the Route's Destination

1. **Click on the route name** to edit it
2. **Check the "Dialplan" section** (you may need to expand it)
3. **Verify the destination:**
   - Should route to: Extension `2001`
   - Or use a Transfer action: `${EXTEN} XML default`

If the route doesn't have a proper destination configured, you need to add one:

1. **Click the route name** to edit
2. **Scroll down to "Dialplan" section**
3. **Click "Add Dialplan Entry"** or edit existing entries
4. **Configure:**
   - **Tag:** `action`
   - **Type:** `transfer`
   - **Data:** `2001 XML default` (or `${EXTEN} XML default` if using variable)
   - **Order:** `10`

### Step 5: Apply Configuration

1. **Click SAVE** on the route
2. **Navigate to:** Status → SIP Status
3. **Click "Reload XML"** button
4. **Or via SSH:**
   ```bash
   fs_cli -x "reloadxml"
   ```

### Step 6: Test the Transfer

After cleanup, test the call transfer again. The call should now route cleanly to extension 2001 without conflicts.

## Why Multiple Routes Cause Problems

1. **Conflicting Orders:** Routes with different orders can interfere with each other
2. **Unpredictable Routing:** FreeSWITCH may route to different routes unpredictably
3. **Debugging Difficulty:** Hard to know which route actually handled the call
4. **Performance:** More routes = more processing time

## Recommended Route Configuration

After cleanup, you should have:

**Single Inbound Route:**
- **Name:** `twilio-to-2001`
- **Number:** `2001`
- **Context:** `public`
- **Order:** `100`
- **Enabled:** `True`
- **Destination:** Extension 2001 (configured in Dialplan section)

**Catch-All Route (keep this):**
- **Name:** `not-found`
- **Context:** `public`
- **Order:** `999` (processes last)
- **Enabled:** `True`
- **Purpose:** Handles calls that don't match other routes

## Verification Commands

After cleanup, verify via SSH:

```bash
# Check inbound routes
sudo -u postgres psql fusionpbx -c "SELECT dialplan_name, dialplan_number, dialplan_context, dialplan_order, dialplan_enabled FROM v_dialplans WHERE dialplan_context = 'public' AND dialplan_name LIKE '%2001%' ORDER BY dialplan_order;"

# Check dialplan routing
fs_cli -x "dialplan show public" | grep -A 5 "2001"

# Reload dialplan
fs_cli -x "reloadxml"
```

You should see only ONE route for 2001 after cleanup.

