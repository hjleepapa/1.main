import asyncio
import logging
import os
from langchain_core.tools import BaseTool
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import InMemorySaver
from typing import List
from dotenv import load_dotenv

from .state import AgentState
from .mcps.local_servers.db_todo import TodoPriority, ReminderImportance
# Optional Composio imports - app should work without them
try:
    from .composio_tools import get_all_integration_tools, test_composio_connection
    COMPOSIO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Composio not available: {e}")
    COMPOSIO_AVAILABLE = False
    def get_all_integration_tools():
        return []
    def test_composio_connection():
        return False
from .redis_manager import redis_manager


load_dotenv()

# Configure logging to suppress HTTP request logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


class TodoAgent:
    def __init__(
            self,
            name: str = "Convonet Assistant",
            model: str = "gpt-4-turbo-preview",
            tools: List[BaseTool] = [],
            system_prompt: str = """You are a productivity assistant that helps users manage todos, reminders, and calendar events. You MUST use tools to perform actions - never just ask for more information.

            CRITICAL RULES:
            1. ALWAYS use tools when users mention creating, adding, or doing something
            2. NEVER ask "what would you like to create?" - infer the intent and use the appropriate tool
            3. Be proactive - if user says "create", "add", "todo", "reminder", "calendar event", immediately use the tool
            4. Make reasonable assumptions when details are missing

            Your messages are read aloud, so be brief and conversational.

            TOOL USAGE GUIDELINES:
            
            PERSONAL PRODUCTIVITY:
            - "create a todo" / "add a task" → use create_todo immediately
            - "create a reminder" → use create_reminder immediately
            - "create/schedule a meeting" / "calendar event" → use create_calendar_event immediately
            - "what are my todos?" / "show todos" → use get_todos immediately
            - "mark [todo] as completed" / "complete [todo]" → use complete_todo immediately
            - "delete todo/reminder/event" → use delete_todo/delete_reminder/delete_calendar_event immediately
            - "update todo/reminder/event" → use update_todo/update_reminder/update_calendar_event immediately
            
            EXTERNAL INTEGRATIONS (via Composio):
            - "send a Slack message" / "message the team" → use Slack tools
            - "create a GitHub issue" / "open a ticket" → use GitHub tools
            - "send an email" / "email someone" → use Gmail tools
            - "create a Notion page" / "add to Notion" → use Notion tools
            - "create a Jira ticket" / "log a bug" → use Jira tools
            - "sync calendar" → use sync_google_calendar_events immediately
            
            TEAM MANAGEMENT:
            - "create a team" / "create [name] team" → use create_team immediately
            - "what teams" / "show teams" / "list teams" → use get_teams immediately
            - "who is in [team]" / "show team members" → use get_team_members immediately
            
            MEMBERSHIP MANAGEMENT:
            - "add [email] to [team]" / "add [email] to [team] as [role]" → use add_team_member immediately
            - "remove [email] from [team]" → use remove_team_member immediately
            - "change [email] to [role]" / "promote [email] to [role]" → use change_member_role immediately
            - "search for [name]" / "find user [name]" → use search_users immediately
            
            TEAM TODO MANAGEMENT:
            - "create todo for [team]" → use create_team_todo immediately
            - "assign [task] to [person] in [team]" → FIRST get_team_members to find user, THEN use create_team_todo
            - "create [priority] todo for [team]" → use create_team_todo immediately
            
            CALL TRANSFER (VOICE CALLS ONLY):
            - "transfer me" / "speak to agent" / "talk to human" → use transfer_to_agent immediately
            - "transfer to [department]" → use transfer_to_agent with department parameter
            - "what departments" / "who can I talk to" → use get_available_departments immediately
            
            CRITICAL RULES FOR TEAM OPERATIONS:
            1. When user mentions a team name, use get_teams to find the exact team_id
            2. When assigning to a person, use get_team_members to find their user_id
            3. Always validate membership before creating team todos
            4. If team name is ambiguous, list available teams and ask for clarification
            5. Default role for new members is "member" unless specified
            
            AUTHENTICATION CONTEXT:
            - authenticated_user_id: The user who made the call (available in state)
            - creator_id: Should be set to authenticated_user_id for all created items
            - When user says "my todos", filter by creator_id or assignee_id = authenticated_user_id

            PRIORITY MAPPING (use these defaults):
            - Shopping/errands: medium priority
            - Work/business: high priority
            - Personal/hobbies: low priority
            - If no priority mentioned: medium priority
            - If no due date mentioned: ALWAYS use today's date (2025-10-17)
            
            CRITICAL: Today's date is 2025-10-17 (October 17, 2025). NEVER use dates from 2023 or 2024. Always use 2025-10-17 as the default date when no specific date is provided.

            <todo_priorities>
            {todo_priorities}
            </todo_priorities>

            <reminder_importance>
            {reminder_importance}
            </reminder_importance>

            <db_schema>
            - todos_convonet (id, created_at, updated_at, title, description, completed, priority, due_date, google_calendar_event_id)
            - reminders_convonet (id, created_at, updated_at, reminder_text, importance, reminder_date, google_calendar_event_id)
            - calendar_events_convonet (id, created_at, updated_at, title, description, event_from, event_to, google_calendar_event_id)
            </db_schema>

            AVAILABLE TOOLS (use them proactively):
            
            PERSONAL PRODUCTIVITY:
            - create_todo: Create personal todos with title, description, priority, due_date
            - get_todos: Get all todos
            - complete_todo: Mark todos as done
            - update_todo: Modify todo properties
            - delete_todo: Remove todos
            - create_reminder: Create reminders with text, importance, date
            - get_reminders: Get all reminders
            - delete_reminder: Remove reminders
            - create_calendar_event: Create events with title, start/end times, description
            - get_calendar_events: Get all events
            - delete_calendar_event: Remove events
            
            TEAM COLLABORATION:
            - create_team: Create a new team with name and description
            - get_teams: List all available teams
            - get_team_members: Get members of a specific team
            - create_team_todo: Create a todo for a team (with optional assignee)
            - add_team_member: Add a user to a team by email with role
            - remove_team_member: Remove a user from a team by email
            - change_member_role: Change a team member's role
            - search_users: Search for users by name or email
            
            DATABASE:
            - query_db: Execute SQL queries
            
            CALL TRANSFER (VOICE CALLS):
            - transfer_to_agent: Transfer call to human agent or department
            - get_available_departments: List available departments for transfer

            EXAMPLES:
            
            PERSONAL PRODUCTIVITY:
            User: "Create a todo for grocery shopping" 
               → IMMEDIATELY use create_todo(title="Grocery shopping", priority="medium", due_date="2025-10-17")
            
            User: "Add Costco shopping to my list" 
               → IMMEDIATELY use create_todo(title="Costco shopping", priority="medium")
            
            User: "Remind me to call mom tomorrow at 2 PM" 
               → IMMEDIATELY use create_reminder(reminder_text="Call mom", reminder_date="2025-10-01T14:00:00", importance="medium")
            
            User: "What are my todos?" 
               → IMMEDIATELY use get_todos()
            
            TEAM CREATION:
            User: "Create a development team" 
               → IMMEDIATELY use create_team(name="Development Team", description="")
            
            User: "Create a hackathon team for our project" 
               → IMMEDIATELY use create_team(name="Hackathon Team", description="Project team")
            
            TEAM DISCOVERY:
            User: "What teams are available?" 
               → IMMEDIATELY use get_teams()
            
            User: "Who is in the development team?" 
               → FIRST use get_teams() to find team_id
               → THEN use get_team_members(team_id)
            
            MEMBERSHIP MANAGEMENT:
            User: "Add john@example.com to the development team as admin" 
               → IMMEDIATELY use add_team_member(team_name="development", email="john@example.com", role="admin")
            
            User: "Remove sarah@example.com from the marketing team" 
               → IMMEDIATELY use remove_team_member(team_name="marketing", email="sarah@example.com")
            
            User: "Change john@example.com to owner role in the dev team" 
               → IMMEDIATELY use change_member_role(team_name="dev", email="john@example.com", new_role="owner")
            
            User: "Search for users named John" 
               → IMMEDIATELY use search_users(search_term="John")
            
            TEAM TODO CREATION (MULTI-STEP):
            User: "Create a high priority todo for the dev team"
               STEP 1: use get_teams() → find team_id for "dev team"
               STEP 2: use create_team_todo(title="Todo", team_id="{{found_id}}", priority="high")
            
            User: "Assign a code review task to John in the development team"
               STEP 1: use get_teams() → find team_id for "development team"
               STEP 2: use get_team_members(team_id) → find user_id for "John"
               STEP 3: use create_team_todo(
                   title="Code review task",
                   team_id="{{team_id}}",
                   assignee_id="{{john_id}}",
                   priority="medium"
               )
            
            User: "Create a demo team meeting tomorrow at 5 PM"
               → IMMEDIATELY use create_calendar_event(
                   title="Demo team meeting",
                   event_from="2025-10-18T17:00:00",
                   event_to="2025-10-18T18:00:00"
               )
            
            COMPLEX TEAM WORKFLOW:
            User: "Create a hackathon team and add admin@convonet.com as owner"
               STEP 1: use create_team(name="Hackathon Team")
               STEP 2: use add_team_member(team_name="Hackathon", email="admin@convonet.com", role="owner")
               STEP 3: Confirm "Hackathon team created and admin@convonet.com added as owner"
            
            CALL TRANSFER EXAMPLES:
            User: "I need to speak to a human"
               → IMMEDIATELY use transfer_to_agent(department="support", reason="User requested human agent")
            
            User: "Transfer me to sales"
               → IMMEDIATELY use transfer_to_agent(department="sales", reason="User requested sales department")
            
            User: "This is too complicated, I need help"
               → IMMEDIATELY use transfer_to_agent(department="support", reason="User needs additional assistance")
            
            User: "What departments can I talk to?"
               → IMMEDIATELY use get_available_departments()
            
            ROLE HIERARCHY:
            - owner: Full control (can delete team, manage all members)
            - admin: Can add/remove members, manage todos
            - member: Can create todos, participate in team
            - viewer: Read-only access to team todos

            Remember: ACT FIRST, ASK LATER. Use tools immediately when you understand the user's intent.
            When dealing with teams, ALWAYS verify team/user existence before operations.
            """,
            ) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.tools = tools

        self.llm = ChatOpenAI(
            name=self.name, 
            model=model,
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.0,  # Lower temperature for more consistent tool calling
        ).bind_tools(tools=self.tools)
        self.graph = self.build_graph()

    def build_graph(self,) -> CompiledStateGraph:
        builder = StateGraph(AgentState)

        async def assistant(state: AgentState):
            """The main assistant node that uses the LLM to generate responses."""
            # inject todo priorities and reminder importance into the system prompt
            system_prompt = self.system_prompt.format(
                todo_priorities=", ".join([p.value for p in TodoPriority]),
                reminder_importance=", ".join([i.value for i in ReminderImportance])
                )

            print(f"🤖 Assistant processing: {state.messages[-1].content if state.messages else 'No messages'}")
            response = await self.llm.ainvoke([SystemMessage(content=system_prompt)] + state.messages)
            print(f"🤖 Assistant response: {response.content}")
            print(f"🤖 Tool calls: {response.tool_calls if hasattr(response, 'tool_calls') else 'None'}")
            print(f"🤖 Available tools: {len(self.tools)}")
            print(f"🤖 Tool names: {[tool.name for tool in self.tools[:5]]}...")  # Show first 5 tools
            
            state.messages.append(response)
            return state

        async def tools_node(state: AgentState):
            """Execute async MCP tools and return results."""
            try:
                print(f"🔧 Tools node executing with {len(self.tools)} tools available")
                
                # Get the last message which should contain tool calls
                last_message = state.messages[-1]
                if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
                    return state
                
                # Execute each tool call
                tool_messages = []
                for tool_call in last_message.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    tool_id = tool_call['id']
                    
                    print(f"🔧 Executing tool: {tool_name} with args: {tool_args}")
                    
                    try:
                        # Find the tool by name
                        tool = None
                        for t in self.tools:
                            if t.name == tool_name:
                                tool = t
                                break
                        
                        if tool:
                            # Execute the async tool with timeout
                            # Reduced timeout to stay under Twilio's 15-second HTTP limit
                            try:
                                if hasattr(tool, 'ainvoke'):
                                    result = await asyncio.wait_for(tool.ainvoke(tool_args), timeout=8.0)
                                else:
                                    result = await asyncio.wait_for(asyncio.to_thread(tool.invoke, tool_args), timeout=8.0)
                                print(f"✅ Tool {tool_name} completed successfully")
                            except asyncio.TimeoutError:
                                result = "I'm sorry, the database operation timed out. Please try again."
                                print(f"⏰ Tool {tool_name} timed out after 8 seconds")
                            except ExceptionGroup as eg:
                                # Unwrap ExceptionGroup and get the first exception
                                print(f"❌ Tool {tool_name} ExceptionGroup with {len(eg.exceptions)} exception(s)")
                                for i, exc in enumerate(eg.exceptions):
                                    print(f"❌   Exception {i+1}: {type(exc).__name__}: {exc}")
                                first_error = eg.exceptions[0] if eg.exceptions else eg
                                error_str = str(first_error)
                                error_type = type(first_error).__name__
                                
                                # Handle BrokenResourceError (MCP connection issue)
                                if "BrokenResourceError" in error_type or not error_str.strip():
                                    result = "I encountered a connection issue with the database. The operation may have completed. Please check your calendar."
                                else:
                                    result = f"I encountered an error: {error_str[:200]}"
                                print(f"❌ Tool {tool_name} error (unwrapped): {error_str if error_str else error_type}")
                            except Exception as tool_error:
                                error_str = str(tool_error)
                                print(f"❌ Tool {tool_name} error: {error_str}")
                                print(f"❌ Tool {tool_name} error type: {type(tool_error)}")
                                
                                # Handle specific error types
                                error_type = type(tool_error).__name__
                                if "BrokenResourceError" in error_type:
                                    result = "I encountered a database connection issue. The operation may have completed. Please check your calendar or todo list."
                                elif "TaskGroup" in error_str:
                                    result = "I encountered a system processing error. The task may have been created successfully. Please check your todo list."
                                elif "Database not available" in error_str or "DB_URI" in error_str:
                                    result = "I'm sorry, there's a database connection issue. Please try again in a moment."
                                elif "validation" in error_str.lower():
                                    result = "I encountered a data validation error. Let me try again."
                                elif not error_str.strip():
                                    # Empty error message
                                    result = "I encountered an unexpected error. Please try again or rephrase your request."
                                else:
                                    result = f"I encountered an error: {error_str[:100]}"
                            
                            from langchain_core.messages import ToolMessage
                            tool_message = ToolMessage(
                                content=str(result),
                                name=tool_name,
                                tool_call_id=tool_id
                            )
                            tool_messages.append(tool_message)
                            print(f"🔧 Tool {tool_name} result: {result}")
                        else:
                            from langchain_core.messages import ToolMessage
                            tool_message = ToolMessage(
                                content=f"Tool {tool_name} not found",
                                name=tool_name,
                                tool_call_id=tool_id
                            )
                            tool_messages.append(tool_message)
                        
                    except Exception as e:
                        error_str = str(e)
                        print(f"❌ Unexpected error in tools_node: {error_str}")
                        print(f"❌ Error type: {type(e)}")
                        from langchain_core.messages import ToolMessage
                        
                        # Handle TaskGroup errors specifically
                        if "TaskGroup" in error_str:
                            error_msg = "I encountered a system processing error. The task may have been created successfully. Please check your todo list."
                        elif "Database not available" in error_str:
                            error_msg = "I'm sorry, there's a temporary database issue. Please try again in a moment."
                        elif "DB_URI" in error_str:
                            error_msg = "I'm sorry, there's a configuration issue with the database. Please try again later."
                        else:
                            error_msg = f"I encountered an error: {error_str[:100]}"
                        
                        tool_message = ToolMessage(
                            content=error_msg,
                            name=tool_name,
                            tool_call_id=tool_id
                        )
                        tool_messages.append(tool_message)
                
                # Add tool messages to state
                state.messages.extend(tool_messages)
                return state
                
            except Exception as e:
                error_str = str(e)
                print(f"❌ Critical error in tools_node: {error_str}")
                print(f"❌ Error type: {type(e)}")
                
                # Return a user-friendly error message
                from langchain_core.messages import ToolMessage
                error_message = ToolMessage(
                    content="I encountered a system processing error. The task may have been created successfully. Please check your todo list.",
                    name="system_error",
                    tool_call_id="error_handling"
                )
                state.messages.append(error_message)
                return state

        builder.add_node(assistant)
        builder.add_node("tools", tools_node)

        builder.set_entry_point("assistant")
        builder.add_conditional_edges(
            "assistant",
            tools_condition
        )
        builder.add_edge("tools", "assistant")

        return builder.compile(checkpointer=InMemorySaver())

    def draw_graph(self,):
        if self.graph is None:
            raise ValueError("Graph not built yet")
        from IPython.display import Image

        return Image(self.graph.get_graph().draw_mermaid_png())

# Lazy initialization to avoid circular imports and environment variable issues
_agent_instance = None

def get_agent():
    """Get or create the TodoAgent instance (lazy initialization)"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TodoAgent()
    return _agent_instance

# For backwards compatibility
agent = None  # Will be initialized on first use

if __name__ == "__main__":
    get_agent().draw_graph()
