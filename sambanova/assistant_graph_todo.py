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


load_dotenv()

# Configure logging to suppress HTTP request logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


class TodoAgent:
    def __init__(
            self,
            name: str = "Sambanova Assistant",
            model: str = "gpt-4o-mini",
            tools: List[BaseTool] = [],
            system_prompt: str = """You are a productivity assistant that helps users manage todos, reminders, and calendar events. You MUST use tools to perform actions - never just ask for more information.

            CRITICAL RULES:
            1. ALWAYS use tools when users mention creating, adding, or doing something
            2. NEVER ask "what would you like to create?" - infer the intent and use the appropriate tool
            3. Be proactive - if user says "create", "add", "todo", "reminder", "calendar event", immediately use the tool
            4. Make reasonable assumptions when details are missing

            Your messages are read aloud, so be brief and conversational.

            TOOL USAGE GUIDELINES:
            - If user says "create a todo" or mentions a task → use create_todo tool immediately
            - If user says "create a reminder" → use create_reminder tool immediately  
            - If user says "create calendar event" → use create_calendar_event tool immediately
            - If user asks "what are my todos?" → use get_todos tool immediately
            - If user wants to complete something → use complete_todo tool immediately

            PRIORITY MAPPING (use these defaults):
            - Shopping/errands: medium priority
            - Work/business: high priority
            - Personal/hobbies: low priority
            - If no priority mentioned: medium priority
            - If no due date mentioned: use today's date

            <todo_priorities>
            {todo_priorities}
            </todo_priorities>

            <reminder_importance>
            {reminder_importance}
            </reminder_importance>

            <db_schema>
            - todos_sambanova (id, created_at, updated_at, title, description, completed, priority, due_date, google_calendar_event_id)
            - reminders_sambanova (id, created_at, updated_at, reminder_text, importance, reminder_date, google_calendar_event_id)
            - calendar_events_sambanova (id, created_at, updated_at, title, description, event_from, event_to, google_calendar_event_id)
            </db_schema>

            AVAILABLE TOOLS (use them proactively):
            - create_todo: Create todos with title, description, priority, due_date
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
            - query_db: Execute SQL queries

            EXAMPLES:
            User: "Create a todo for grocery shopping" → IMMEDIATELY use create_todo with title="Grocery shopping", priority="medium", due_date=today
            User: "Add Costco shopping to my list" → IMMEDIATELY use create_todo with title="Costco shopping", priority="medium", due_date=today
            User: "Create a reminder for the meeting" → IMMEDIATELY use create_reminder with reasonable defaults
            User: "What are my todos?" → IMMEDIATELY use get_todos tool

            Remember: ACT FIRST, ASK LATER. Use tools immediately when you understand the user's intent.
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

        def assistant(state: AgentState):
            """The main assistant node that uses the LLM to generate responses."""
            # inject todo priorities and reminder importance into the system prompt
            system_prompt = self.system_prompt.format(
                todo_priorities=", ".join([p.value for p in TodoPriority]),
                reminder_importance=", ".join([i.value for i in ReminderImportance])
                )

            print(f"🤖 Assistant processing: {state.messages[-1].content if state.messages else 'No messages'}")
            response = self.llm.invoke([SystemMessage(content=system_prompt)] + state.messages)
            print(f"🤖 Assistant response: {response.content}")
            print(f"🤖 Tool calls: {response.tool_calls if hasattr(response, 'tool_calls') else 'None'}")
            
            state.messages.append(response)
            return state

        def tools_node(state: AgentState):
            """Execute tools and return results."""
            print(f"🔧 Tools node executing with {len(self.tools)} tools available")
            tool_node = ToolNode(self.tools)
            result = tool_node.invoke(state)
            print(f"🔧 Tools result: {result}")
            return result

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

agent = TodoAgent()

if __name__ == "__main__":
    agent.draw_graph()
