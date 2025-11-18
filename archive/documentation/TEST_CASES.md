# Convonet Team Collaboration System - Test Cases

## 🧪 Complete Test Suite

---

## 1. PIN Authentication Tests

### Test Case 1.1: DTMF PIN Entry (Keypad)
**Objective**: Verify keypad PIN authentication works

**Prerequisites**: 
- Admin user exists with PIN '1234'

**Steps**:
1. Call Twilio number
2. Wait for prompt: "Please enter or say your 4 to 6 digit PIN, then press pound"
3. Press: `1`, `2`, `3`, `4`, `#` on phone keypad

**Expected Result**: 
- ✅ System says: "Welcome back, Admin! How can I help you today?"
- ✅ User is authenticated for the session

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 1.2: Speech PIN Entry (Voice)
**Objective**: Verify spoken PIN authentication works

**Prerequisites**: 
- Admin user exists with PIN '1234'

**Steps**:
1. Call Twilio number
2. Wait for prompt
3. Say out loud: "one two three four"

**Expected Result**: 
- ✅ System says: "Welcome back, Admin! How can I help you today?"
- ✅ User is authenticated

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 1.3: Invalid PIN
**Objective**: Verify system rejects incorrect PIN

**Steps**:
1. Call Twilio number
2. Press: `9`, `9`, `9`, `9`, `#`

**Expected Result**: 
- ✅ System says: "Invalid PIN. Please try again."
- ✅ Redirects back to PIN prompt
- ✅ User is NOT authenticated

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 1.4: PIN Too Short
**Objective**: Verify system rejects PINs under 4 digits

**Steps**:
1. Call Twilio number
2. Press: `1`, `2`, `3`, `#`

**Expected Result**: 
- ✅ System says: "Invalid PIN format. Please enter a 4 to 6 digit PIN."
- ✅ Redirects back to PIN prompt

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 1.5: PIN Too Long
**Objective**: Verify system rejects PINs over 6 digits

**Steps**:
1. Call Twilio number
2. Press: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `#`

**Expected Result**: 
- ✅ System says: "Invalid PIN format. Please enter a 4 to 6 digit PIN."
- ✅ Redirects back to PIN prompt

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

## 2. Personal Productivity Tests

### Test Case 2.1: Create Simple Todo
**Objective**: Create a basic todo via voice

**Prerequisites**: 
- User authenticated (PIN entered)

**Steps**:
1. After authentication, say: "Create a todo to buy groceries"

**Expected Result**: 
- ✅ System confirms: "I've created a todo titled 'Buy groceries'"
- ✅ Todo appears in database with default priority (medium)
- ✅ Todo has today's date as due date
- ✅ Google Calendar event created

**Database Verification**:
```sql
SELECT title, priority, due_date, google_calendar_event_id 
FROM todos_convonet 
WHERE title ILIKE '%groceries%' 
ORDER BY created_at DESC LIMIT 1;
```

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 2.2: Create Todo with Priority
**Objective**: Create a high priority todo

**Steps**:
1. Say: "Create a high priority todo to finish the project report"

**Expected Result**: 
- ✅ Todo created with priority = 'high'
- ✅ System mentions priority in confirmation

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 2.3: Create Todo with Due Date
**Objective**: Create todo with specific due date

**Steps**:
1. Say: "Create a todo to call mom tomorrow at 2 PM"

**Expected Result**: 
- ✅ Todo created with due_date = tomorrow at 14:00
- ✅ Google Calendar event at correct time

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 2.4: List All Todos
**Objective**: Retrieve all todos for authenticated user

**Steps**:
1. Say: "What are my todos?" or "Show me my todos"

**Expected Result**: 
- ✅ System lists all todos
- ✅ Includes title and priority for each
- ✅ Indicates completed status

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 2.5: Complete a Todo
**Objective**: Mark todo as completed

**Prerequisites**:
- At least one incomplete todo exists

**Steps**:
1. Say: "Mark 'buy groceries' as complete"

**Expected Result**: 
- ✅ Todo marked as completed in database
- ✅ System confirms completion

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 2.6: Create Reminder
**Objective**: Create a reminder with date

**Steps**:
1. Say: "Remind me to take medicine tomorrow at 9 AM"

**Expected Result**: 
- ✅ Reminder created in database
- ✅ Google Calendar event created
- ✅ Importance set to default (medium)

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 2.7: Create Calendar Event
**Objective**: Create a calendar event with time range

**Steps**:
1. Say: "Create a meeting on October 15th from 2 PM to 3 PM"

**Expected Result**: 
- ✅ Calendar event created
- ✅ Event duration = 1 hour
- ✅ Google Calendar sync successful

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

## 3. Team Management Tests

### Test Case 3.1: List Available Teams
**Objective**: Get list of all teams

**Steps**:
1. Say: "What teams are available?" or "Show me all teams"

**Expected Result**: 
- ✅ System lists all active teams
- ✅ Includes team names and IDs
- ✅ Shows creation dates

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 3.2: Get Team Members
**Objective**: List members of a specific team

**Prerequisites**:
- At least one team exists with members

**Steps**:
1. Say: "Who is in the development team?"

**Expected Result**: 
- ✅ System lists all team members
- ✅ Shows roles for each member
- ✅ Shows join dates

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 3.3: Create New Team
**Objective**: Create a team via voice command

**Steps**:
1. Say: "Create a team called Marketing"

**Expected Result**: 
- ✅ Team created in database
- ✅ System provides team ID
- ✅ Team marked as active

**Database Verification**:
```sql
SELECT id, name, description, is_active 
FROM teams_convonet 
WHERE name = 'Marketing' 
ORDER BY created_at DESC LIMIT 1;
```

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 3.4: Add Team Member with Default Role
**Objective**: Add user to team with default member role

**Prerequisites**:
- User admin@convonet.com exists
- Team "Marketing" exists

**Steps**:
1. Say: "Add admin@convonet.com to the Marketing team"

**Expected Result**: 
- ✅ User added to team
- ✅ Role = 'member' (default)
- ✅ System confirms addition

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 3.5: Add Team Member with Specific Role
**Objective**: Add user to team with admin role

**Steps**:
1. Say: "Add admin@convonet.com to the Marketing team as admin"

**Expected Result**: 
- ✅ User added to team
- ✅ Role = 'admin'
- ✅ System confirms with role

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 3.6: Search for Users
**Objective**: Find users by name or email

**Steps**:
1. Say: "Search for users named John"

**Expected Result**: 
- ✅ System lists matching users
- ✅ Shows email and username
- ✅ Shows user IDs

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 3.7: Remove Team Member
**Objective**: Remove a user from a team

**Prerequisites**:
- User is a member of the team
- User is not the last owner

**Steps**:
1. Say: "Remove john@example.com from the Marketing team"

**Expected Result**: 
- ✅ Membership deleted
- ✅ System confirms removal
- ✅ User can no longer access team todos

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 3.8: Change Member Role
**Objective**: Update a team member's role

**Steps**:
1. Say: "Change john@example.com's role to admin in the Marketing team"

**Expected Result**: 
- ✅ Role updated in database
- ✅ System confirms old role → new role
- ✅ User gains admin permissions

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 3.9: Prevent Removing Last Owner
**Objective**: System should prevent removing the last owner

**Prerequisites**:
- Team has exactly one owner

**Steps**:
1. Say: "Remove [last-owner-email] from the team"

**Expected Result**: 
- ✅ System rejects the operation
- ✅ Error message: "Cannot remove the last owner from the team. Assign another owner first."
- ✅ Membership not deleted

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

## 4. Team Todo Tests

### Test Case 4.1: Create Simple Team Todo
**Objective**: Create a todo for a team

**Prerequisites**:
- Team "Marketing" exists

**Steps**:
1. Say: "Create a todo for the Marketing team to prepare the campaign"

**Expected Result**: 
- ✅ Todo created with team_id set
- ✅ System confirms team association
- ✅ Todo visible to all team members

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 4.2: Create Team Todo with Priority
**Objective**: Create high priority team todo

**Steps**:
1. Say: "Create a high priority todo for the Marketing team to review the budget"

**Expected Result**: 
- ✅ Todo created with priority = 'high'
- ✅ Team_id set correctly
- ✅ Google Calendar event created

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 4.3: Assign Team Todo to Member
**Objective**: Create todo assigned to specific team member

**Prerequisites**:
- User john@example.com is a member of Marketing team

**Steps**:
1. Say: "Assign a task to John in the Marketing team to write the blog post"

**Expected Result**: 
- ✅ Todo created with team_id
- ✅ Assignee_id = John's user ID
- ✅ System confirms assignee
- ✅ John can see the todo assigned to him

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 4.4: Create Team Todo for Non-Existent Team
**Objective**: Verify error handling for invalid team

**Steps**:
1. Say: "Create a todo for the NonExistent team"

**Expected Result**: 
- ✅ System responds: "Team 'NonExistent' not found"
- ✅ No todo created
- ✅ Suggests available teams

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 4.5: Assign Todo to Non-Member
**Objective**: Verify validation of team membership

**Prerequisites**:
- User external@example.com is NOT a member of Marketing team

**Steps**:
1. Say: "Assign a task to external@example.com in the Marketing team"

**Expected Result**: 
- ✅ System responds: "User external@example.com is not a member of team 'Marketing'"
- ✅ No todo created
- ✅ Suggests using get_team_members first

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

## 5. Multi-Step Workflow Tests

### Test Case 5.1: Create Team and Add Members
**Objective**: Test complex workflow

**Steps**:
1. Say: "Create a team called Engineering"
2. Wait for confirmation
3. Say: "Add admin@convonet.com to the Engineering team as owner"
4. Wait for confirmation
5. Say: "Add john@example.com to the Engineering team as member"

**Expected Result**: 
- ✅ Team created successfully
- ✅ Admin added as owner
- ✅ John added as member
- ✅ All memberships verified in database

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 5.2: Find Team and Create Todo
**Objective**: Test team lookup + todo creation

**Steps**:
1. Say: "What teams are available?"
2. Note team names from response
3. Say: "Create a high priority todo for the Engineering team to deploy the app"

**Expected Result**: 
- ✅ System finds team from previous context
- ✅ Todo created with correct team_id
- ✅ Priority set to high

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 5.3: Find User and Assign Task
**Objective**: Test user search + assignment

**Steps**:
1. Say: "Search for users named John"
2. Note John's email from response
3. Say: "Assign a code review task to john@example.com in the Engineering team"

**Expected Result**: 
- ✅ User found successfully
- ✅ Team membership verified
- ✅ Todo created and assigned
- ✅ Task visible to John

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

## 6. Google Calendar Integration Tests

### Test Case 6.1: Todo Syncs to Calendar
**Objective**: Verify todo creates Google Calendar event

**Steps**:
1. Create todo via voice: "Create a todo to review code tomorrow at 3 PM"
2. Check database for google_calendar_event_id
3. Open Google Calendar

**Expected Result**: 
- ✅ google_calendar_event_id is not null
- ✅ Event appears in Google Calendar
- ✅ Event title: "Todo: Review code"
- ✅ Event time: Tomorrow at 3 PM
- ✅ Duration: 1 hour

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 6.2: Reminder Syncs to Calendar
**Objective**: Verify reminder creates calendar event

**Steps**:
1. Say: "Remind me to call the client tomorrow at 10 AM"
2. Check Google Calendar

**Expected Result**: 
- ✅ Event appears with title: "Reminder: Call the client"
- ✅ Event time: Tomorrow at 10 AM
- ✅ Duration: 30 minutes
- ✅ Description includes importance level

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 6.3: Calendar Event Direct Sync
**Objective**: Verify calendar events sync

**Steps**:
1. Say: "Schedule a team standup on Monday at 9 AM for 30 minutes"
2. Check Google Calendar

**Expected Result**: 
- ✅ Event appears with exact title
- ✅ Correct start time and end time
- ✅ Event visible in primary calendar

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 6.4: Delete Todo Deletes Calendar Event
**Objective**: Verify cascading delete to calendar

**Prerequisites**:
- Todo exists with google_calendar_event_id

**Steps**:
1. Note the google_calendar_event_id
2. Delete the todo: "Delete the 'buy groceries' todo"
3. Check Google Calendar

**Expected Result**: 
- ✅ Todo deleted from database
- ✅ Calendar event also deleted
- ✅ Event no longer visible in Google Calendar

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

## 7. Web Dashboard Tests

### Test Case 7.1: User Registration
**Objective**: Register new user via web

**Steps**:
1. Go to https://hjlees.com/register
2. Fill in:
   - Email: test@example.com
   - Username: testuser
   - First Name: Test
   - Last Name: User
   - Password: SecurePass123
   - Confirm Password: SecurePass123
   - Voice PIN: 5678
3. Click "Create Account"

**Expected Result**: 
- ✅ User created in database
- ✅ Password hashed with bcrypt
- ✅ Voice PIN stored
- ✅ Redirect to login or dashboard

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 7.2: User Login
**Objective**: Login via web dashboard

**Steps**:
1. Go to https://hjlees.com/team-dashboard
2. Enter:
   - Email: admin@convonet.com
   - Password: admin123
3. Click "Login"

**Expected Result**: 
- ✅ JWT token generated
- ✅ Token stored in localStorage
- ✅ Dashboard loads
- ✅ Teams dropdown populates

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 7.3: Create Team via Dashboard
**Objective**: Create team using web UI

**Prerequisites**:
- User logged in

**Steps**:
1. Click "Create New Team" button
2. Fill in:
   - Team Name: Sales Team
   - Description: Sales and customer relations
3. Click "Create Team"

**Expected Result**: 
- ✅ Team appears in dropdown
- ✅ User automatically added as owner
- ✅ Success message shown

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 7.4: Add Team Member via Dashboard
**Objective**: Add member using web UI

**Steps**:
1. Select team from dropdown
2. Click "Add Member"
3. Search for user
4. Select role (Member, Admin, Viewer)
5. Click "Add Member"

**Expected Result**: 
- ✅ Member added to team
- ✅ Member appears in team list
- ✅ Correct role displayed

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 7.5: Create Todo via Dashboard
**Objective**: Create todo using web UI

**Steps**:
1. Select team from dropdown
2. Click "Create Todo"
3. Fill in:
   - Title: Test todo
   - Description: This is a test
   - Priority: High
   - Due Date: Tomorrow
4. Click "Create Todo"

**Expected Result**: 
- ✅ Todo appears in todo list
- ✅ Google Calendar event created
- ✅ Todo visible to all team members

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 7.6: JWT Token Expiry
**Objective**: Verify token expiry handling

**Steps**:
1. Login to dashboard
2. Wait 24+ hours (or manually expire token)
3. Try to load teams

**Expected Result**: 
- ✅ API returns 401 Unauthorized
- ✅ User logged out automatically
- ✅ Redirect to login page
- ✅ Error message shown

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

## 8. Error Handling Tests

### Test Case 8.1: Network Timeout
**Objective**: Verify graceful timeout handling

**Steps**:
1. Simulate slow network (DevTools throttling)
2. Try to create a todo via voice

**Expected Result**: 
- ✅ System waits up to 30 seconds
- ✅ If timeout, says: "I'm sorry, I'm taking too long. Please try again."
- ✅ No partial data created

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 8.2: Database Connection Error
**Objective**: Verify database error handling

**Steps**:
1. Temporarily stop database (or simulate)
2. Try to create a todo

**Expected Result**: 
- ✅ System detects database unavailable
- ✅ Says: "I'm having a temporary system issue"
- ✅ Logs error for debugging

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 8.3: Google Calendar API Failure
**Objective**: Verify calendar sync error handling

**Steps**:
1. Revoke calendar permissions (or simulate)
2. Create a todo

**Expected Result**: 
- ✅ Todo still created in database
- ✅ google_calendar_event_id remains null
- ✅ System continues without blocking
- ✅ User notified of sync issue

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 8.4: Ambiguous Voice Input
**Objective**: Verify clarification requests

**Steps**:
1. Say something ambiguous: "Create a thing"

**Expected Result**: 
- ✅ System asks for clarification
- ✅ "What would you like me to create? A todo, reminder, or calendar event?"
- ✅ Waits for clarification

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 8.5: Unsupported Command
**Objective**: Verify handling of unknown requests

**Steps**:
1. Say something the system doesn't support: "Tell me a joke"

**Expected Result**: 
- ✅ System responds politely
- ✅ "I'm a productivity assistant. I can help you with todos, reminders, calendar events, and team management."
- ✅ Suggests available features

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

## 9. Performance Tests

### Test Case 9.1: Response Time
**Objective**: Measure typical response time

**Steps**:
1. Call and authenticate
2. Say: "Create a todo to test performance"
3. Measure time from end of speech to start of response

**Expected Result**: 
- ✅ Response within 3-5 seconds
- ✅ No noticeable delay
- ✅ Natural conversation flow

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 9.2: Concurrent Users
**Objective**: Test multiple simultaneous calls

**Steps**:
1. Have 3-5 people call simultaneously
2. Each creates todos

**Expected Result**: 
- ✅ All calls handled successfully
- ✅ No cross-talk between sessions
- ✅ Each user's todos correctly attributed
- ✅ No database deadlocks

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 9.3: Large Team Performance
**Objective**: Test with team of 50+ members

**Prerequisites**:
- Create team with 50 members

**Steps**:
1. Say: "Who is in the [large team]?"
2. Measure response time

**Expected Result**: 
- ✅ Response within 5-7 seconds
- ✅ All members listed
- ✅ No timeout errors

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

## 10. Security Tests

### Test Case 10.1: SQL Injection Prevention
**Objective**: Verify input sanitization

**Steps**:
1. Try to create todo with malicious title: "Test'; DROP TABLE todos_convonet; --"

**Expected Result**: 
- ✅ Input treated as literal string
- ✅ No SQL injection occurs
- ✅ Todo created with exact title
- ✅ Tables remain intact

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 10.2: Authentication Bypass Attempt
**Objective**: Verify PIN security

**Steps**:
1. Call and enter wrong PIN 5 times
2. Try various PINs

**Expected Result**: 
- ✅ Each wrong PIN rejected
- ✅ No lockout (yet - future feature)
- ✅ No access without correct PIN
- ✅ User data remains protected

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 10.3: JWT Token Tampering
**Objective**: Verify JWT signature validation

**Steps**:
1. Login to web dashboard
2. Get JWT token from localStorage
3. Modify user_id in token payload
4. Make API request with tampered token

**Expected Result**: 
- ✅ API rejects request
- ✅ 401 Unauthorized returned
- ✅ Error: "Invalid token signature"
- ✅ No unauthorized access granted

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 10.4: Cross-Team Data Isolation
**Objective**: Verify users can't access other teams' data

**Prerequisites**:
- User A is member of Team 1 only
- User B is member of Team 2 only

**Steps**:
1. User A logs in
2. User A tries to access Team 2's todos

**Expected Result**: 
- ✅ API returns empty list or 403 Forbidden
- ✅ User A cannot see Team 2 data
- ✅ Data isolation enforced

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

## 11. Edge Case Tests

### Test Case 11.1: Empty Team Name
**Objective**: Verify validation of team name

**Steps**:
1. Say: "Create a team called" (pause, don't say name)

**Expected Result**: 
- ✅ System prompts: "What would you like to name the team?"
- ✅ Waits for team name
- ✅ No team created without name

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 11.2: Very Long Todo Title
**Objective**: Test limits on input length

**Steps**:
1. Say a todo with 500+ character title

**Expected Result**: 
- ✅ System accepts input (or truncates gracefully)
- ✅ Todo created successfully
- ✅ No database errors

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 11.3: Special Characters in Names
**Objective**: Test Unicode and special character handling

**Steps**:
1. Create todo with emojis: "Create a todo to review the 🚀 launch"
2. Create team with accents: "Create team called Café"

**Expected Result**: 
- ✅ Characters preserved correctly
- ✅ Display properly in database and UI
- ✅ No encoding errors

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 11.4: Duplicate Team Names
**Objective**: Verify handling of duplicate team names

**Steps**:
1. Create team: "Create a team called Marketing"
2. Create again: "Create a team called Marketing"

**Expected Result**: 
- ✅ Either:
  - Second team created with different ID, OR
  - System warns: "Team 'Marketing' already exists"
- ✅ Clear handling of duplicates

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

### Test Case 11.5: Call Interruption
**Objective**: Test call disconnect handling

**Steps**:
1. Start creating a todo
2. Hang up mid-conversation

**Expected Result**: 
- ✅ Partial data not saved (or saved with incomplete flag)
- ✅ No database corruption
- ✅ Next call starts fresh

**Actual Result**: _____________________

**Status**: ⬜ Pass ⬜ Fail

---

## 📊 Test Summary Template

| Category | Total | Passed | Failed | Pending |
|----------|-------|--------|--------|---------|
| Authentication | 5 | ___ | ___ | ___ |
| Personal Productivity | 7 | ___ | ___ | ___ |
| Team Management | 9 | ___ | ___ | ___ |
| Team Todos | 5 | ___ | ___ | ___ |
| Multi-Step Workflows | 3 | ___ | ___ | ___ |
| Google Calendar | 4 | ___ | ___ | ___ |
| Web Dashboard | 6 | ___ | ___ | ___ |
| Error Handling | 5 | ___ | ___ | ___ |
| Performance | 3 | ___ | ___ | ___ |
| Security | 4 | ___ | ___ | ___ |
| Edge Cases | 5 | ___ | ___ | ___ |
| **TOTAL** | **56** | **___** | **___** | **___** |

---

## 🎯 Priority Test Cases (Must Pass)

**Critical (Must work for demo)**:
1. Test Case 1.1 - DTMF PIN Entry ⭐⭐⭐
2. Test Case 2.1 - Create Simple Todo ⭐⭐⭐
3. Test Case 3.1 - List Available Teams ⭐⭐⭐
4. Test Case 4.1 - Create Team Todo ⭐⭐⭐
5. Test Case 6.1 - Calendar Sync ⭐⭐⭐
6. Test Case 7.2 - Web Login ⭐⭐⭐

**High Priority (Important features)**:
- Test Cases 1.2, 2.2, 2.3, 3.3, 3.4, 4.2, 7.1, 7.3

**Medium Priority (Nice to have)**:
- All other test cases

---

## 📝 Test Execution Notes

**Test Environment**:
- URL: https://hjlees.com
- Phone Number: [Your Twilio Number]
- Database: PostgreSQL on Render.com
- Test User: admin@convonet.com / admin123 / PIN: 1234

**Test Execution Date**: _______________

**Tester Name**: _______________

**Build Version**: _______________

**Additional Notes**:
_________________________________________________
_________________________________________________
_________________________________________________

---

**Generated for Convonet Team Collaboration System**  
*Last Updated: October 2025*

