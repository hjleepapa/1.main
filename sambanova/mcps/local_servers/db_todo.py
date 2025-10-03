from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import List, Optional
from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
import os
from pydantic import BaseModel
from enum import StrEnum
import pandas as pd
# Google Calendar integration
try:
    from google_calendar import get_calendar_service
except ImportError:
    # Fallback for when running as MCP server
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    try:
        from google_calendar import get_calendar_service
    except ImportError:
        print("⚠️  Warning: Google Calendar integration not available - google_calendar module not found")
        get_calendar_service = None

# Service Account Google Calendar integration
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import base64
    import pickle
    import json
    
    def get_service_account_calendar_service():
        """Get Google Calendar service using service account credentials"""
        try:
            # Check for base64 encoded credentials in environment
            if os.getenv('GOOGLE_CREDENTIALS_B64'):
                print("🔧 Using GOOGLE_CREDENTIALS_B64 environment variable")
                creds_data = base64.b64decode(os.getenv('GOOGLE_CREDENTIALS_B64'))
                creds = service_account.Credentials.from_service_account_info(
                    json.loads(creds_data.decode('utf-8')),
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
            # Check for base64 encoded token in environment
            elif os.getenv('GOOGLE_TOKEN_B64'):
                print("🔧 Using GOOGLE_TOKEN_B64 environment variable")
                token_data = base64.b64decode(os.getenv('GOOGLE_TOKEN_B64'))
                creds = pickle.loads(token_data)
                if hasattr(creds, 'refresh_token') and creds.expired:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
            # Check for local credentials.json file
            elif os.path.exists('credentials.json'):
                print("🔧 Using local credentials.json file")
                creds = service_account.Credentials.from_service_account_file(
                    'credentials.json',
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
            else:
                print("❌ No Google Calendar credentials found")
                return None
                
            service = build('calendar', 'v3', credentials=creds)
            print("✅ Google Calendar service created successfully")
            return service
            
        except Exception as e:
            print(f"❌ Error creating Google Calendar service: {e}")
            return None
            
    # Override the original get_calendar_service function
    get_calendar_service = get_service_account_calendar_service
    
except ImportError as e:
    print(f"⚠️  Warning: Google Calendar service account integration not available: {e}")
    get_service_account_calendar_service = None

load_dotenv()

# ----------------------------
# SQLAlchemy Models
# ----------------------------

class Base(DeclarativeBase):
     pass


class DBTodo(Base):
    __tablename__ = "todos_sambanova"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, server_default=text("gen_random_uuid()"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"), onupdate=datetime.now)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    completed: Mapped[bool] = mapped_column(nullable=False, server_default=text("false"))
    priority: Mapped[str] = mapped_column(String, nullable=False, server_default=text("medium"))
    due_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    google_calendar_event_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class DBReminder(Base):
    __tablename__ = "reminders_sambanova"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, server_default=text("gen_random_uuid()"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"), onupdate=datetime.now)
    reminder_text: Mapped[str] = mapped_column(String, nullable=False)
    importance: Mapped[str] = mapped_column(String, nullable=False, server_default=text("medium"))
    reminder_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    google_calendar_event_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class DBCalendarEvent(Base):
    __tablename__ = "calendar_events_sambanova"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, server_default=text("gen_random_uuid()"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"), onupdate=datetime.now)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    event_from: Mapped[datetime] = mapped_column(nullable=False)
    event_to: Mapped[datetime] = mapped_column(nullable=False)
    google_calendar_event_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class DBCallRecording(Base):
    __tablename__ = "call_recordings_sambanova"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, server_default=text("gen_random_uuid()"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
    call_sid: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    from_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    to_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    recording_path: Mapped[str] = mapped_column(String, nullable=False)
    duration_seconds: Mapped[Optional[int]] = mapped_column(nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(nullable=True)
    transcription: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'completed'"))  # completed, failed, processing 

# ----------------------------
# Pydantic Models
# ----------------------------

class TodoPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Todo(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    title: str
    description: Optional[str]
    completed: bool
    priority: TodoPriority
    due_date: Optional[datetime]
    google_calendar_event_id: Optional[str]


class ReminderImportance(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Reminder(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    reminder_text: str
    importance: ReminderImportance
    reminder_date: Optional[datetime]
    google_calendar_event_id: Optional[str]


class CalendarEvent(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    title: str
    description: Optional[str]
    event_from: datetime
    event_to: datetime
    google_calendar_event_id: Optional[str]


class CallRecording(BaseModel):
    id: UUID
    created_at: datetime
    call_sid: str
    from_number: Optional[str]
    to_number: Optional[str]
    recording_path: str
    duration_seconds: Optional[int]
    file_size_bytes: Optional[int]
    transcription: Optional[str]
    status: str

# ----------------------------
# DB Session
# ----------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Lazy database connection - don't connect at import time
db_uri = os.getenv("DB_URI")
engine = None
SessionLocal = None
_db_initialized = False

def _init_database():
    """Initialize database connection (lazy loading)."""
    global engine, SessionLocal, _db_initialized
    
    if _db_initialized:
        return
    
    _db_initialized = True
    
    if not db_uri:
        print("⚠️  Warning: DB_URI not set, MCP server database operations will be disabled")
        return
    
    try:
        print("🔄 Initializing database connection...")
        # Create engine with very aggressive timeout settings
        engine = create_engine(
            url=db_uri,
            pool_pre_ping=False,  # Skip pre-ping to avoid hanging
            pool_size=1,  # Minimal pool for MCP server
            max_overflow=0,  # No overflow
            pool_timeout=1,  # 1 second timeout
            pool_recycle=1800,  # Recycle connections every 30 mins
            connect_args={"connect_timeout": 1}  # 1 second connection timeout
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print("✅ Database connection configured successfully (no test)")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        engine = None
        SessionLocal = None

# ----------------------------
# Helper Functions
# ----------------------------

def check_database_available():
    """Check if database is available."""
    try:
        _init_database()  # Lazy init on first use
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        raise Exception(f"Database initialization failed: {str(e)}")
    
    if SessionLocal is None:
        raise Exception("Database not available - DB_URI not configured")

# ----------------------------
# MCP Server
# ----------------------------

mcp = FastMCP("db_todo")

@mcp.tool()
async def test_connection() -> str:
    """Test if the MCP server is working."""
    print("🔧 MCP test_connection: Function called")
    return "MCP server is working!"

@mcp.tool()
async def simple_test() -> str:
    """Simple test without database."""
    print("🔧 MCP simple_test: Function called")
    return "Simple test successful!"

@mcp.tool()
async def test_google_calendar() -> str:
    """Test Google Calendar service availability and credentials."""
    try:
        print("🔧 Testing Google Calendar service...")
        
        # Check if get_calendar_service is available
        if not get_calendar_service:
            return "❌ Google Calendar service not available - get_calendar_service is None"
        
        print("✅ get_calendar_service function is available")
        
        # Try to get the calendar service
        try:
            calendar_service = get_calendar_service()
            print(f"✅ Calendar service obtained: {calendar_service}")
            
            # Try to create a test event
            test_event_id = calendar_service.create_event(
                title="Test Event",
                description="This is a test event to verify Google Calendar integration",
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc) + timedelta(minutes=15)
            )
            
            if test_event_id:
                print(f"✅ Test event created successfully with ID: {test_event_id}")
                
                # Try to delete the test event
                try:
                    success = calendar_service.delete_event(test_event_id)
                    if success:
                        print(f"✅ Test event deleted successfully")
                        return f"✅ Google Calendar service is working correctly!\nTest event created and deleted: {test_event_id}"
                    else:
                        return f"⚠️  Google Calendar service created event but failed to delete it: {test_event_id}"
                except Exception as delete_error:
                    return f"⚠️  Google Calendar service created event but delete failed: {delete_error}"
            else:
                return "❌ Google Calendar service failed to create test event - returned None"
                
        except Exception as service_error:
            print(f"❌ Error getting calendar service: {service_error}")
            return f"❌ Google Calendar service error: {service_error}"
            
    except Exception as e:
        error_msg = f"Error testing Google Calendar: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@mcp.tool()
async def test_database() -> str:
    """Test database connection only."""
    try:
        print("🔧 MCP test_database: Starting")
        check_database_available()
        print("🔧 MCP test_database: Database available")
        
        with SessionLocal() as session:
            print("🔧 MCP test_database: Session created")
            result = session.execute(text("SELECT 1 as test")).fetchone()
            print(f"🔧 MCP test_database: Query result: {result}")
            return f"Database test successful: {result[0]}"
    except Exception as e:
        print(f"❌ MCP test_database: Error: {e}")
        return f"Database test failed: {str(e)}"

@mcp.tool()
async def create_todo(
    title: str,
    description: Optional[str] = None,
    priority: TodoPriority = TodoPriority.MEDIUM,
    due_date: Optional[datetime] = None,
    ) -> str:
    """Create a new todo item.
    
    Args:
        title: The title of the todo item.
        description: An optional description of the todo item.
        priority: The priority level of the todo. Options are: low, medium, high, urgent
        due_date: The due date for the todo item. If not specified, will automatically default to today's date.

    Returns:
        The created todo item.
    """
    try:
        print(f"🔧 MCP create_todo: Starting with title='{title}', priority={priority}")
        print(f"🔧 MCP create_todo: Checking database availability...")
        check_database_available()
        print(f"🔧 MCP create_todo: Database available, creating session...")
        
        with SessionLocal() as session:
            print(f"🔧 MCP create_todo: Session created, setting due date...")
            # Set default due date to today if not provided
            if due_date is None:
                due_date = datetime.now(timezone.utc)
                
            print(f"🔧 MCP create_todo: Creating DBTodo object...")
            new_todo = DBTodo(
                title=title,
                description=description,
                priority=priority.value,
                due_date=due_date,
                )
            print(f"🔧 MCP create_todo: Adding todo to session...")
            session.add(new_todo)
            print(f"🔧 MCP create_todo: Committing to database...")
            session.commit()
            print(f"🔧 MCP create_todo: Refreshing object...")
            session.refresh(new_todo)
            print(f"🔧 MCP create_todo: Todo created successfully with ID: {new_todo.id}")
            
            # Create corresponding Google Calendar event
            google_event_id = None
            print(f"🔧 MCP create_todo: Checking Google Calendar service availability...")
            print(f"🔧 MCP create_todo: get_calendar_service = {get_calendar_service}")
            
            if get_calendar_service:
                try:
                    print(f"🔧 MCP create_todo: Creating Google Calendar event...")
                    calendar_service = get_calendar_service()
                    print(f"🔧 MCP create_todo: Calendar service obtained: {calendar_service}")
                    
                    # Use due_date as the event start time, with 1 hour duration
                    event_start = due_date
                    event_end = due_date + timedelta(hours=1)
                    print(f"🔧 MCP create_todo: Event times - start: {event_start}, end: {event_end}")
                    
                    google_event_id = calendar_service.create_event(
                        title=f"Todo: {title}",
                        description=description or "",
                        start_time=event_start,
                        end_time=event_end
                    )
                    print(f"🔧 MCP create_todo: Calendar service returned: {google_event_id}")
                    
                    if google_event_id:
                        print(f"✅ MCP create_todo: Google Calendar event created with ID: {google_event_id}")
                        # Update the todo with the Google Calendar event ID
                        new_todo.google_calendar_event_id = google_event_id
                        session.commit()
                        session.refresh(new_todo)
                    else:
                        print(f"⚠️  MCP create_todo: Failed to create Google Calendar event - returned None")
                except Exception as calendar_error:
                    print(f"⚠️  MCP create_todo: Google Calendar error (continuing): {calendar_error}")
                    print(f"⚠️  MCP create_todo: Error type: {type(calendar_error)}")
            else:
                print(f"⚠️  MCP create_todo: Google Calendar service not available - get_calendar_service is None")
    
        # Convert SQLAlchemy object to dict properly
        todo_dict = {
            "id": str(new_todo.id),
            "created_at": new_todo.created_at.isoformat(),
            "updated_at": new_todo.updated_at.isoformat(),
            "title": new_todo.title,
            "description": new_todo.description,
            "completed": new_todo.completed,
            "priority": new_todo.priority,
            "due_date": new_todo.due_date.isoformat() if new_todo.due_date else None,
            "google_calendar_event_id": new_todo.google_calendar_event_id
        }
        result = Todo.model_validate(todo_dict).model_dump_json(indent=2)
        print(f"✅ MCP create_todo: Successfully created todo '{title}'")
        return result
        
    except Exception as e:
        error_msg = f"Error executing tool create_todo: {str(e)}"
        print(f"❌ MCP create_todo: {error_msg}")
        return error_msg

@mcp.tool()
async def get_todos() -> str:
    """Get all todo items.
    
    Returns:
        A list of all todo items.
    """
    with SessionLocal() as session:
        todos = session.query(DBTodo).all()
        todos_list = [Todo.model_validate(todo.__dict__).model_dump_json(indent=2) for todo in todos]
    return f"[{', \n'.join(todos_list)}]"

@mcp.tool()
async def complete_todo(id: UUID) -> str:
    """Mark a todo item as completed.
    
    Args:
        id: The id of the todo item to complete.

    Returns:
        The updated todo item.
    """
    with SessionLocal() as session:
        todo = session.query(DBTodo).filter(DBTodo.id == id).first()
        if not todo:
            return "Todo not found"
        
        todo.completed = True
        session.commit()
        
        # Google Calendar sync disabled
        print(f"✅ Todo '{todo.title}' marked as completed")
        
        session.refresh(todo)
    
    return Todo.model_validate(todo.__dict__).model_dump_json(indent=2)

@mcp.tool()
async def update_todo(
    id: UUID,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[TodoPriority] = None,
    due_date: Optional[datetime] = None,
    completed: Optional[bool] = None,
    ) -> str:
    """Update a todo item by id.
    
    Args:
        id: The id of the todo item to update.
        title: The new title of the todo item.
        description: The new description of the todo item.
        priority: The new priority level of the todo. Options are: low, medium, high, urgent
        due_date: The new due date for the todo item.
        completed: The new completion status of the todo item.

    Returns:
        The updated todo item.
    """
    with SessionLocal() as session:
        todo = session.query(DBTodo).filter(DBTodo.id == id).first()
        if not todo:
            return "Todo not found"
        
        if title:
            todo.title = title
        if description is not None:
            todo.description = description
        if priority:
            todo.priority = priority.value
        if due_date is not None:
            todo.due_date = due_date
        if completed is not None:
            todo.completed = completed

        session.commit()
        session.refresh(todo)
        
        # Update Google Calendar event if it exists
        if todo.google_calendar_event_id and get_calendar_service:
            try:
                print(f"🔧 MCP update_todo: Updating Google Calendar event: {todo.google_calendar_event_id}")
                calendar_service = get_calendar_service()
                
                # Prepare update data
                update_data = {}
                if title:
                    update_data['title'] = f"Todo: {title}"
                if description is not None:
                    update_data['description'] = description or ""
                if due_date is not None:
                    update_data['start_time'] = due_date
                    update_data['end_time'] = due_date + timedelta(hours=1)
                
                if update_data:
                    success = calendar_service.update_event(
                        event_id=todo.google_calendar_event_id,
                        **update_data
                    )
                    if success:
                        print(f"✅ MCP update_todo: Google Calendar event updated successfully")
                    else:
                        print(f"⚠️  MCP update_todo: Failed to update Google Calendar event")
                else:
                    print(f"ℹ️  MCP update_todo: No calendar-relevant fields updated")
            except Exception as calendar_error:
                print(f"⚠️  MCP update_todo: Google Calendar error (continuing): {calendar_error}")
    
    return Todo.model_validate(todo.__dict__).model_dump_json(indent=2)

@mcp.tool()
async def delete_todo(id: UUID) -> str:
    """Delete a todo item by id.
    
    Args:
        id: The id of the todo item to delete.

    Returns:
        The deleted todo item.
    """
    with SessionLocal() as session:
        todo = session.query(DBTodo).filter(DBTodo.id == id).first()
        if not todo:
            return "Todo not found"
        
        print(f"🗑️ Deleting todo: {todo.title}")
        
        # Delete from Google Calendar if event exists
        if todo.google_calendar_event_id and get_calendar_service:
            try:
                print(f"🔧 MCP delete_todo: Deleting Google Calendar event: {todo.google_calendar_event_id}")
                calendar_service = get_calendar_service()
                success = calendar_service.delete_event(todo.google_calendar_event_id)
                if success:
                    print(f"✅ MCP delete_todo: Google Calendar event deleted successfully")
                else:
                    print(f"⚠️  MCP delete_todo: Failed to delete Google Calendar event")
            except Exception as calendar_error:
                print(f"⚠️  MCP delete_todo: Google Calendar error (continuing): {calendar_error}")
        
        session.delete(todo)
        session.commit()
    
    return Todo.model_validate(todo.__dict__).model_dump_json(indent=2)

@mcp.tool()
async def create_reminder(
    reminder_text: str,
    importance: ReminderImportance = ReminderImportance.MEDIUM,
    reminder_date: Optional[datetime] = None,
    ) -> str:
    """Create a new reminder.
    
    Args:
        reminder_text: The text content of the reminder.
        importance: The importance level of the reminder. Options are: low, medium, high, urgent
        reminder_date: An optional date/time for the reminder.

    Returns:
        The created reminder.
    """
    try:
        print(f"🔧 MCP create_reminder: Starting with text='{reminder_text}', importance={importance}")
        check_database_available()
        
        with SessionLocal() as session:
            # Handle both string and enum inputs for importance
            importance_value = importance.value if hasattr(importance, 'value') else importance
            
            new_reminder = DBReminder(
                reminder_text=reminder_text,
                importance=importance_value,
                reminder_date=reminder_date,
                )
            session.add(new_reminder)
            session.commit()
            session.refresh(new_reminder)
            print(f"🔧 MCP create_reminder: Reminder created successfully with ID: {new_reminder.id}")
            
            # Create corresponding Google Calendar event
            google_event_id = None
            if get_calendar_service:
                try:
                    print(f"🔧 MCP create_reminder: Creating Google Calendar event...")
                    calendar_service = get_calendar_service()
                    
                    # Use reminder_date as the event start time, with 30 minutes duration
                    event_start = reminder_date or datetime.now(timezone.utc)
                    event_end = event_start + timedelta(minutes=30)
                    
                    google_event_id = calendar_service.create_event(
                        title=f"Reminder: {reminder_text}",
                        description=f"Reminder - Importance: {importance_value}",
                        start_time=event_start,
                        end_time=event_end
                    )
                    
                    if google_event_id:
                        print(f"✅ MCP create_reminder: Google Calendar event created with ID: {google_event_id}")
                        # Update the reminder with the Google Calendar event ID
                        new_reminder.google_calendar_event_id = google_event_id
                        session.commit()
                        session.refresh(new_reminder)
                    else:
                        print(f"⚠️  MCP create_reminder: Failed to create Google Calendar event")
                except Exception as calendar_error:
                    print(f"⚠️  MCP create_reminder: Google Calendar error (continuing): {calendar_error}")
            else:
                print(f"⚠️  MCP create_reminder: Google Calendar service not available")
    
        # Convert SQLAlchemy object to dict properly
        reminder_dict = {
            "id": str(new_reminder.id),
            "created_at": new_reminder.created_at.isoformat(),
            "updated_at": new_reminder.updated_at.isoformat(),
            "reminder_text": new_reminder.reminder_text,
            "importance": new_reminder.importance,
            "reminder_date": new_reminder.reminder_date.isoformat() if new_reminder.reminder_date else None,
            "google_calendar_event_id": new_reminder.google_calendar_event_id
        }
        result = Reminder.model_validate(reminder_dict).model_dump_json(indent=2)
        print(f"✅ MCP create_reminder: Successfully created reminder '{reminder_text}'")
        return result
        
    except Exception as e:
        error_msg = f"Error executing tool create_reminder: {str(e)}"
        print(f"❌ MCP create_reminder: {error_msg}")
        return error_msg

@mcp.tool()
async def get_reminders() -> str:
    """Get all reminders.
    
    Returns:
        A list of all reminders.
    """
    with SessionLocal() as session:
        reminders = session.query(DBReminder).all()
        reminders_list = [Reminder.model_validate(reminder.__dict__).model_dump_json(indent=2) for reminder in reminders]
    return f"[{', \n'.join(reminders_list)}]"

@mcp.tool()
async def update_reminder(
    id: UUID,
    reminder_text: Optional[str] = None,
    importance: Optional[ReminderImportance] = None,
    reminder_date: Optional[datetime] = None,
    ) -> str:
    """Update a reminder by id.
    
    Args:
        id: The id of the reminder to update.
        reminder_text: The new text content of the reminder.
        importance: The new importance level of the reminder. Options are: low, medium, high, urgent
        reminder_date: The new date/time for the reminder.

    Returns:
        The updated reminder.
    """
    with SessionLocal() as session:
        reminder = session.query(DBReminder).filter(DBReminder.id == id).first()
        if not reminder:
            return "Reminder not found"
        
        if reminder_text:
            reminder.reminder_text = reminder_text
        if importance:
            reminder.importance = importance.value
        if reminder_date is not None:
            reminder.reminder_date = reminder_date

        session.commit()
        session.refresh(reminder)
        
        # Update Google Calendar event if it exists
        if reminder.google_calendar_event_id and get_calendar_service:
            try:
                print(f"🔧 MCP update_reminder: Updating Google Calendar event: {reminder.google_calendar_event_id}")
                calendar_service = get_calendar_service()
                
                # Prepare update data
                update_data = {}
                if reminder_text:
                    update_data['title'] = f"Reminder: {reminder_text}"
                if importance:
                    update_data['description'] = f"Reminder - Importance: {importance.value}"
                if reminder_date is not None:
                    update_data['start_time'] = reminder_date
                    update_data['end_time'] = reminder_date + timedelta(minutes=30)
                
                if update_data:
                    success = calendar_service.update_event(
                        event_id=reminder.google_calendar_event_id,
                        **update_data
                    )
                    if success:
                        print(f"✅ MCP update_reminder: Google Calendar event updated successfully")
                    else:
                        print(f"⚠️  MCP update_reminder: Failed to update Google Calendar event")
                else:
                    print(f"ℹ️  MCP update_reminder: No calendar-relevant fields updated")
            except Exception as calendar_error:
                print(f"⚠️  MCP update_reminder: Google Calendar error (continuing): {calendar_error}")
    
    return Reminder.model_validate(reminder.__dict__).model_dump_json(indent=2)

@mcp.tool()
async def delete_reminder(id: UUID) -> str:
    """Delete a reminder by id.
    
    Args:
        id: The id of the reminder to delete.

    Returns:
        The deleted reminder.
    """
    with SessionLocal() as session:
        reminder = session.query(DBReminder).filter(DBReminder.id == id).first()
        if not reminder:
            return "Reminder not found"
        
        print(f"🗑️ Deleting reminder: {reminder.reminder_text}")
        
        # Delete from Google Calendar if event exists
        if reminder.google_calendar_event_id and get_calendar_service:
            try:
                print(f"🔧 MCP delete_reminder: Deleting Google Calendar event: {reminder.google_calendar_event_id}")
                calendar_service = get_calendar_service()
                success = calendar_service.delete_event(reminder.google_calendar_event_id)
                if success:
                    print(f"✅ MCP delete_reminder: Google Calendar event deleted successfully")
                else:
                    print(f"⚠️  MCP delete_reminder: Failed to delete Google Calendar event")
            except Exception as calendar_error:
                print(f"⚠️  MCP delete_reminder: Google Calendar error (continuing): {calendar_error}")
        
        session.delete(reminder)
        session.commit()
    
    return Reminder.model_validate(reminder.__dict__).model_dump_json(indent=2)

@mcp.tool()
async def create_calendar_event(
    title: str,
    event_from: datetime,
    event_to: datetime,
    description: Optional[str] = None,
    ) -> str:
    """Create a new calendar event.
    
    Args:
        title: The title of the calendar event.
        event_from: The start date and time of the event.
        event_to: The end date and time of the event.
        description: An optional description of the event.

    Returns:
        The created calendar event.
    """
    try:
        print(f"🔧 MCP create_calendar_event: Starting with title='{title}'")
        check_database_available()
        
        with SessionLocal() as session:
            new_event = DBCalendarEvent(
                title=title,
                description=description,
                event_from=event_from,
                event_to=event_to,
                )
            session.add(new_event)
            session.commit()
            session.refresh(new_event)
            print(f"🔧 MCP create_calendar_event: Event created successfully with ID: {new_event.id}")
            
            # Create corresponding Google Calendar event
            google_event_id = None
            if get_calendar_service:
                try:
                    print(f"🔧 MCP create_calendar_event: Creating Google Calendar event...")
                    calendar_service = get_calendar_service()
                    
                    google_event_id = calendar_service.create_event(
                        title=title,
                        description=description or "",
                        start_time=event_from,
                        end_time=event_to
                    )
                    
                    if google_event_id:
                        print(f"✅ MCP create_calendar_event: Google Calendar event created with ID: {google_event_id}")
                        # Update the event with the Google Calendar event ID
                        new_event.google_calendar_event_id = google_event_id
                        session.commit()
                        session.refresh(new_event)
                    else:
                        print(f"⚠️  MCP create_calendar_event: Failed to create Google Calendar event")
                except Exception as calendar_error:
                    print(f"⚠️  MCP create_calendar_event: Google Calendar error (continuing): {calendar_error}")
            else:
                print(f"⚠️  MCP create_calendar_event: Google Calendar service not available")
    
        result = CalendarEvent.model_validate(new_event.__dict__).model_dump_json(indent=2)
        print(f"✅ MCP create_calendar_event: Successfully created event '{title}'")
        return result
        
    except Exception as e:
        error_msg = f"Error executing tool create_calendar_event: {str(e)}"
        print(f"❌ MCP create_calendar_event: {error_msg}")
        return error_msg

@mcp.tool()
async def get_calendar_events() -> str:
    """Get all calendar events.
    
    Returns:
        A list of all calendar events.
    """
    with SessionLocal() as session:
        events = session.query(DBCalendarEvent).all()
        events_list = [CalendarEvent.model_validate(event.__dict__).model_dump_json(indent=2) for event in events]
    return f"[{', \n'.join(events_list)}]"

@mcp.tool()
async def update_calendar_event(
    id: UUID,
    title: Optional[str] = None,
    event_from: Optional[datetime] = None,
    event_to: Optional[datetime] = None,
    description: Optional[str] = None,
    ) -> str:
    """Update a calendar event by id.
    
    Args:
        id: The id of the calendar event to update.
        title: The new title of the calendar event.
        event_from: The new start date and time of the event.
        event_to: The new end date and time of the event.
        description: The new description of the event.

    Returns:
        The updated calendar event.
    """
    with SessionLocal() as session:
        event = session.query(DBCalendarEvent).filter(DBCalendarEvent.id == id).first()
        if not event:
            return "Calendar event not found"
        
        if title:
            event.title = title
        if event_from is not None:
            event.event_from = event_from
        if event_to is not None:
            event.event_to = event_to
        if description is not None:
            event.description = description

        session.commit()
        session.refresh(event)
        
        # Update Google Calendar event if it exists
        if event.google_calendar_event_id and get_calendar_service:
            try:
                print(f"🔧 MCP update_calendar_event: Updating Google Calendar event: {event.google_calendar_event_id}")
                calendar_service = get_calendar_service()
                
                # Prepare update data
                update_data = {}
                if title:
                    update_data['title'] = title
                if description is not None:
                    update_data['description'] = description or ""
                if event_from is not None:
                    update_data['start_time'] = event_from
                if event_to is not None:
                    update_data['end_time'] = event_to
                
                if update_data:
                    success = calendar_service.update_event(
                        event_id=event.google_calendar_event_id,
                        **update_data
                    )
                    if success:
                        print(f"✅ MCP update_calendar_event: Google Calendar event updated successfully")
                    else:
                        print(f"⚠️  MCP update_calendar_event: Failed to update Google Calendar event")
                else:
                    print(f"ℹ️  MCP update_calendar_event: No calendar-relevant fields updated")
            except Exception as calendar_error:
                print(f"⚠️  MCP update_calendar_event: Google Calendar error (continuing): {calendar_error}")
    
    return CalendarEvent.model_validate(event.__dict__).model_dump_json(indent=2)

@mcp.tool()
async def delete_calendar_event(id: UUID) -> str:
    """Delete a calendar event by id.
    
    Args:
        id: The id of the calendar event to delete.

    Returns:
        The deleted calendar event.
    """
    with SessionLocal() as session:
        event = session.query(DBCalendarEvent).filter(DBCalendarEvent.id == id).first()
        if not event:
            return "Calendar event not found"
        
        print(f"🗑️ Deleting calendar event: {event.title}")
        
        # Delete from Google Calendar if event exists
        if event.google_calendar_event_id and get_calendar_service:
            try:
                print(f"🔧 MCP delete_calendar_event: Deleting Google Calendar event: {event.google_calendar_event_id}")
                calendar_service = get_calendar_service()
                success = calendar_service.delete_event(event.google_calendar_event_id)
                if success:
                    print(f"✅ MCP delete_calendar_event: Google Calendar event deleted successfully")
                else:
                    print(f"⚠️  MCP delete_calendar_event: Failed to delete Google Calendar event")
            except Exception as calendar_error:
                print(f"⚠️  MCP delete_calendar_event: Google Calendar error (continuing): {calendar_error}")
        
        session.delete(event)
        session.commit()
    
    return CalendarEvent.model_validate(event.__dict__).model_dump_json(indent=2)

@mcp.tool()
async def create_call_recording(
    call_sid: str,
    recording_path: str,
    from_number: Optional[str] = None,
    to_number: Optional[str] = None,
    duration_seconds: Optional[int] = None,
    file_size_bytes: Optional[int] = None,
    transcription: Optional[str] = None,
    status: str = "completed"
) -> str:
    """Create a new call recording record.
    
    Args:
        call_sid: Twilio Call SID (unique identifier)
        recording_path: Path to the audio recording file
        from_number: Caller's phone number
        to_number: Called phone number
        duration_seconds: Duration of the recording in seconds
        file_size_bytes: Size of the recording file in bytes
        transcription: Text transcription of the call
        status: Recording status (completed, failed, processing)

    Returns:
        The created call recording record
    """
    with SessionLocal() as session:
        recording = DBCallRecording(
            call_sid=call_sid,
            recording_path=recording_path,
            from_number=from_number,
            to_number=to_number,
            duration_seconds=duration_seconds,
            file_size_bytes=file_size_bytes,
            transcription=transcription,
            status=status
        )
        session.add(recording)
        session.commit()
        session.refresh(recording)
    
    return CallRecording.model_validate(recording.__dict__).model_dump_json(indent=2)

@mcp.tool()
async def get_call_recordings() -> str:
    """Get all call recordings.
    
    Returns:
        A list of all call recordings
    """
    with SessionLocal() as session:
        recordings = session.query(DBCallRecording).order_by(DBCallRecording.created_at.desc()).all()
    
    return [CallRecording.model_validate(recording.__dict__).model_dump() for recording in recordings]

@mcp.tool()
async def get_call_recording_by_sid(call_sid: str) -> str:
    """Get a call recording by Call SID.
    
    Args:
        call_sid: Twilio Call SID to search for

    Returns:
        The call recording record or error message
    """
    with SessionLocal() as session:
        recording = session.query(DBCallRecording).filter(DBCallRecording.call_sid == call_sid).first()
        
        if not recording:
            return f"Call recording with SID {call_sid} not found"
    
    return CallRecording.model_validate(recording.__dict__).model_dump_json(indent=2)

@mcp.tool()
async def update_call_recording(
    call_sid: str,
    transcription: Optional[str] = None,
    status: Optional[str] = None,
    duration_seconds: Optional[int] = None,
    file_size_bytes: Optional[int] = None
) -> str:
    """Update a call recording record.
    
    Args:
        call_sid: Twilio Call SID to update
        transcription: Updated transcription text
        status: Updated recording status
        duration_seconds: Updated duration in seconds
        file_size_bytes: Updated file size in bytes

    Returns:
        The updated call recording record
    """
    with SessionLocal() as session:
        recording = session.query(DBCallRecording).filter(DBCallRecording.call_sid == call_sid).first()
        
        if not recording:
            return f"Call recording with SID {call_sid} not found"
        
        if transcription is not None:
            recording.transcription = transcription
        if status is not None:
            recording.status = status
        if duration_seconds is not None:
            recording.duration_seconds = duration_seconds
        if file_size_bytes is not None:
            recording.file_size_bytes = file_size_bytes
            
        session.commit()
        session.refresh(recording)
    
    return CallRecording.model_validate(recording.__dict__).model_dump_json(indent=2)

@mcp.tool()
async def delete_call_recording(call_sid: str) -> str:
    """Delete a call recording by Call SID.
    
    Args:
        call_sid: Twilio Call SID to delete

    Returns:
        Success message or error
    """
    with SessionLocal() as session:
        recording = session.query(DBCallRecording).filter(DBCallRecording.call_sid == call_sid).first()
        
        if not recording:
            return f"Call recording with SID {call_sid} not found"
        
        # Delete the actual file if it exists
        try:
            if os.path.exists(recording.recording_path):
                os.remove(recording.recording_path)
        except Exception as e:
            return f"Error deleting file: {str(e)}"
        
        session.delete(recording)
        session.commit()
    
    return f"Call recording {call_sid} deleted successfully"

@mcp.tool()
async def query_db(query: str) -> str:
    """Query the database using SQL.
    
    Args:
        query: A valid PostgreSQL query to run.

    Returns:
        The query results
    """
    with SessionLocal() as session:
        result = session.execute(text(query))
        
    return pd.DataFrame(result.all(), columns=result.keys()).to_json(orient="records", indent=2)

@mcp.tool()
async def sync_google_calendar_events() -> str:
    """Sync all existing todos, reminders, and calendar events with Google Calendar.
    
    This function will create Google Calendar events for any items that don't already have
    a google_calendar_event_id. Useful for syncing existing data.
    
    Returns:
        Summary of sync operations performed.
    """
    try:
        print("🔄 Starting Google Calendar sync for existing items...")
        check_database_available()
        
        if not get_calendar_service:
            return "Google Calendar service not available. Please check your Google Calendar configuration."
        
        calendar_service = get_calendar_service()
        sync_summary = {
            "todos_processed": 0,
            "todos_created": 0,
            "reminders_processed": 0,
            "reminders_created": 0,
            "events_processed": 0,
            "events_created": 0,
            "errors": []
        }
        
        with SessionLocal() as session:
            # Sync todos
            print("🔧 Syncing todos...")
            todos = session.query(DBTodo).filter(DBTodo.google_calendar_event_id.is_(None)).all()
            for todo in todos:
                sync_summary["todos_processed"] += 1
                try:
                    # Use due_date as the event start time, with 1 hour duration
                    event_start = todo.due_date or datetime.now(timezone.utc)
                    event_end = event_start + timedelta(hours=1)
                    
                    google_event_id = calendar_service.create_event(
                        title=f"Todo: {todo.title}",
                        description=todo.description or "",
                        start_time=event_start,
                        end_time=event_end
                    )
                    
                    if google_event_id:
                        todo.google_calendar_event_id = google_event_id
                        sync_summary["todos_created"] += 1
                        print(f"✅ Created Google Calendar event for todo: {todo.title}")
                    else:
                        sync_summary["errors"].append(f"Failed to create calendar event for todo: {todo.title}")
                        print(f"⚠️  Failed to create calendar event for todo: {todo.title}")
                except Exception as e:
                    error_msg = f"Error syncing todo '{todo.title}': {str(e)}"
                    sync_summary["errors"].append(error_msg)
                    print(f"❌ {error_msg}")
            
            # Sync reminders
            print("🔧 Syncing reminders...")
            reminders = session.query(DBReminder).filter(DBReminder.google_calendar_event_id.is_(None)).all()
            for reminder in reminders:
                sync_summary["reminders_processed"] += 1
                try:
                    # Use reminder_date as the event start time, with 30 minutes duration
                    event_start = reminder.reminder_date or datetime.now(timezone.utc)
                    event_end = event_start + timedelta(minutes=30)
                    
                    google_event_id = calendar_service.create_event(
                        title=f"Reminder: {reminder.reminder_text}",
                        description=f"Reminder - Importance: {reminder.importance}",
                        start_time=event_start,
                        end_time=event_end
                    )
                    
                    if google_event_id:
                        reminder.google_calendar_event_id = google_event_id
                        sync_summary["reminders_created"] += 1
                        print(f"✅ Created Google Calendar event for reminder: {reminder.reminder_text}")
                    else:
                        sync_summary["errors"].append(f"Failed to create calendar event for reminder: {reminder.reminder_text}")
                        print(f"⚠️  Failed to create calendar event for reminder: {reminder.reminder_text}")
                except Exception as e:
                    error_msg = f"Error syncing reminder '{reminder.reminder_text}': {str(e)}"
                    sync_summary["errors"].append(error_msg)
                    print(f"❌ {error_msg}")
            
            # Sync calendar events
            print("🔧 Syncing calendar events...")
            events = session.query(DBCalendarEvent).filter(DBCalendarEvent.google_calendar_event_id.is_(None)).all()
            for event in events:
                sync_summary["events_processed"] += 1
                try:
                    google_event_id = calendar_service.create_event(
                        title=event.title,
                        description=event.description or "",
                        start_time=event.event_from,
                        end_time=event.event_to
                    )
                    
                    if google_event_id:
                        event.google_calendar_event_id = google_event_id
                        sync_summary["events_created"] += 1
                        print(f"✅ Created Google Calendar event for calendar event: {event.title}")
                    else:
                        sync_summary["errors"].append(f"Failed to create calendar event for: {event.title}")
                        print(f"⚠️  Failed to create calendar event for: {event.title}")
                except Exception as e:
                    error_msg = f"Error syncing calendar event '{event.title}': {str(e)}"
                    sync_summary["errors"].append(error_msg)
                    print(f"❌ {error_msg}")
            
            # Commit all changes
            session.commit()
            print("✅ All changes committed to database")
        
        # Generate summary
        summary = f"""Google Calendar Sync Complete!

📊 Summary:
- Todos processed: {sync_summary['todos_processed']}, created: {sync_summary['todos_created']}
- Reminders processed: {sync_summary['reminders_processed']}, created: {sync_summary['reminders_created']}
- Calendar events processed: {sync_summary['events_processed']}, created: {sync_summary['events_created']}
- Errors: {len(sync_summary['errors'])}

✅ Total Google Calendar events created: {sync_summary['todos_created'] + sync_summary['reminders_created'] + sync_summary['events_created']}"""

        if sync_summary['errors']:
            summary += f"\n\n❌ Errors encountered:\n" + "\n".join(sync_summary['errors'])
        
        print(summary)
        return summary
        
    except Exception as e:
        error_msg = f"Error during Google Calendar sync: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg


if __name__ == "__main__":
    mcp.run(transport="stdio")
