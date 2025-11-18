# Slack + Composio Integration for Todo Tasks

## 🚀 **Slack Integration Overview**

The Convonet project integrates with Slack through Composio to enable voice-controlled todo task management and team communication.

## 📋 **Available Slack Functions:**

### **1. Primary Slack Function: `SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL`**

This is the main function that sends todo tasks to Slack channels.

#### **Function Details:**
- **Name**: `SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL`
- **Purpose**: Send messages (including todo tasks) to Slack channels
- **Authentication**: Requires Slack App OAuth setup
- **Parameters**:
  - `channel`: Slack channel ID or name
  - `text`: Message content (todo task details)
  - `mrkdwn`: Enable markdown formatting (boolean)

#### **Usage Example:**
```python
# Send a todo task to Slack
message_params = {
    "channel": "general",  # or channel ID
    "text": "📋 New Todo: Complete Redis integration review\nPriority: High\nDue: Today",
    "mrkdwn": True
}

toolset.execute_action(
    action=Action.SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL,
    parameters=message_params
)
```

### **2. Additional Slack Functions Available:**

Based on Composio's Slack integration, other functions may include:
- **Channel Management**: Create channels, list channels
- **User Management**: Get user info, list team members
- **Message Management**: Send direct messages, reply to messages
- **File Sharing**: Upload files, share documents

## 🎯 **Todo Task Flow to Slack:**

### **Voice Command → Slack Integration:**

#### **1. Voice Input:**
```
User: "Send a todo task to the dev team about reviewing the Redis integration"
```

#### **2. Agent Processing:**
1. **Intent Recognition**: Agent identifies Slack messaging intent
2. **Tool Selection**: Selects `SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL`
3. **Parameter Extraction**: Extracts channel, message content
4. **Action Execution**: Calls Composio Slack function

#### **3. Slack Message Sent:**
```
Channel: #dev-team
Message: 📋 New Todo Task
Title: Review Redis Integration
Priority: High
Assigned: Development Team
Due: Today
```

## 🔧 **Implementation Details:**

### **1. Composio Configuration:**
```python
# Environment variables
COMPOSIO_API_KEY=ak_68Xsj6WGv3Zl4ooBgkcD
COMPOSIO_PROJECT_ID=pr_bz7nkY2wflSi

# Slack App configuration (in Composio dashboard)
SLACK_CLIENT_ID=your_slack_app_client_id
SLACK_CLIENT_SECRET=your_slack_app_client_secret
```

### **2. Authentication Setup:**
1. **Create Slack App**: In Slack API dashboard
2. **Configure OAuth**: Set redirect URLs and scopes
3. **Composio Integration**: Connect Slack app to Composio
4. **User Authorization**: Users authorize Slack access

### **3. Tool Integration in Agent:**
```python
# In convonet/routes.py
try:
    from .composio_tools import get_all_integration_tools, test_composio_connection
    if test_composio_connection():
        composio_tools = get_all_integration_tools()
        tools.extend(composio_tools)  # Includes Slack tools
        print(f"✅ Added {len(composio_tools)} Composio integration tools")
```

## 🎵 **Voice Commands for Slack:**

### **Todo Task Commands:**
- *"Send a todo to the dev team about fixing the login bug"*
- *"Message the team about the high-priority database issue"*
- *"Post a todo in the general channel for code review"*
- *"Send a reminder to the marketing team about the campaign deadline"*

### **Team Communication Commands:**
- *"Send a message to the dev team about the new feature"*
- *"Notify the team about the server maintenance"*
- *"Post an update in the project channel"*

## 📊 **Message Formatting:**

### **Todo Task Message Template:**
```
📋 **New Todo Task**
**Title**: {todo_title}
**Description**: {todo_description}
**Priority**: {priority}
**Due Date**: {due_date}
**Assigned To**: {assignee}
**Created By**: {creator}
```

### **Example Slack Message:**
```
📋 **New Todo Task**
**Title**: Review Redis Integration
**Description**: Test Redis session management and caching functionality
**Priority**: High
**Due Date**: Today (2025-10-25)
**Assigned To**: Development Team
**Created By**: Admin
```

## 🔄 **Integration Flow:**

### **1. Voice Assistant Flow:**
```
User Voice → Speech-to-Text → Agent Processing → Slack Tool Selection → Composio API → Slack Channel
```

### **2. Technical Flow:**
```
WebRTC Audio → Whisper API → LangGraph Agent → Composio Slack Tools → Slack API → Channel Message
```

### **3. Error Handling:**
- **Authentication Errors**: Graceful fallback, user notification
- **Channel Not Found**: Suggest available channels
- **Permission Denied**: Request proper Slack permissions
- **Network Issues**: Retry mechanism with user feedback

## 🎯 **Use Cases:**

### **1. Team Todo Management:**
- **Daily Standups**: Send daily todo lists to team channels
- **Project Updates**: Notify team about new tasks and priorities
- **Deadline Reminders**: Send urgent todo reminders

### **2. Project Coordination:**
- **Bug Reports**: Send bug-related todos to development channels
- **Feature Requests**: Post feature todos to product channels
- **Code Reviews**: Send review todos to code review channels

### **3. Cross-Team Communication:**
- **Marketing Campaigns**: Send campaign todos to marketing teams
- **Sales Tasks**: Post sales-related todos to sales channels
- **Support Issues**: Send support todos to customer service teams

## 🚀 **Benefits:**

### **1. Voice-Controlled Team Communication:**
- **Natural Language**: Use voice commands for team messaging
- **Hands-Free**: No need to type or use keyboard
- **Multi-Channel**: Send to different teams and channels

### **2. Integrated Todo Management:**
- **Unified System**: Todos in both personal system and Slack
- **Team Visibility**: Team members see todos in Slack
- **Real-Time Updates**: Instant notifications in Slack channels

### **3. Enhanced Collaboration:**
- **Transparent Communication**: All team members see todos
- **Priority Visibility**: Clear priority indicators in messages
- **Assignment Tracking**: Know who's responsible for what

## 🔧 **Setup Requirements:**

### **1. Slack App Setup:**
- **Bot Token**: For sending messages
- **OAuth Scopes**: `chat:write`, `channels:read`, `users:read`
- **Event Subscriptions**: For receiving messages (optional)

### **2. Composio Configuration:**
- **API Key**: `ak_68Xsj6WGv3Zl4ooBgkcD`
- **Project ID**: `pr_bz7nkY2wflSi`
- **Slack App Connection**: OAuth flow completion

### **3. Environment Variables:**
```bash
COMPOSIO_API_KEY=ak_68Xsj6WGv3Zl4ooBgkcD
COMPOSIO_PROJECT_ID=pr_bz7nkY2wflSi
SLACK_CLIENT_ID=your_slack_app_client_id
SLACK_CLIENT_SECRET=your_slack_app_client_secret
```

## 📈 **Demo Scenarios:**

### **1. Hackathon Demo:**
```
"Hey Convonet, create a high-priority todo to review Redis integration, 
assign it to John, and send a Slack message to the dev-team channel 
saying 'Redis integration is ready for review'"
```

### **2. Daily Standup:**
```
"Send today's todo list to the standup channel with our top 3 priorities"
```

### **3. Bug Report:**
```
"Create a bug todo for the login issue and notify the dev team in Slack"
```

## 🎉 **Result:**

The Slack integration enables seamless voice-controlled todo task management with team communication, allowing users to create todos and immediately notify team members through Slack channels using natural language voice commands! 🚀📋
