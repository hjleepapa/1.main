import json
import datetime as dt
import os
from dotenv import load_dotenv
from typing import Union, Dict, Any
from contextlib import contextmanager
from typing import Generator

from pydantic import BaseModel, ValidationError as PydanticValidationError

from flask import Blueprint, request, jsonify, abort
from sqlalchemy import Column, Integer, String, Boolean, DateTime
#from sqlalchemy.orm import Session # Keep for type hinting if needed

from extensions import db # Import the shared db instance
#from sqlalchemy.orm import sessionmaker

# Create a session factory bound to the shared db engine
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db.engine)

# Load environment variables from .env file
# Ensure .env is in the root of "1. Main" or adjust path accordingly if vapi_todo is run standalone
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env') # Assumes .env is in "1. Main"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # Fallback if .env is next to this file (e.g. if vapi_todo is a separate project)
    load_dotenv()

# Flask Blueprint
vapi_flask_bp = Blueprint('vapi_flask', __name__, url_prefix='/vapi_project')

# --- SQLAlchemy Models  ---
class Todo(db.Model): # Inherit from the shared db.Model
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)

class Reminder(db.Model): # Inherit from the shared db.Model
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True, index=True)
    reminder_text = Column(String)
    importance = Column(String)

class CalendarEvent(db.Model): # Inherit from the shared db.Model
    __tablename__ = 'calendar_events'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    event_from = Column(DateTime)
    event_to = Column(DateTime)

# Create tables if they don't exist.
# This is generally fine. If integrated into a larger Flask app that also calls
# create_all on the same Base/metadata, SQLAlchemy handles it gracefully.
# db.create_all()

#@contextmanager
# def get_db_session() -> Generator[Session, None, None]:
#     """Provides a SQLAlchemy session within a context manager."""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#         db.close()

# --- Pydantic Models  ---
class ToolCallFunction(BaseModel):
    name: str
    arguments: Union[str, Dict[str, Any]] # Using Dict for parsed JSON

class ToolCall(BaseModel):
    id: str
    function: ToolCallFunction

class Message(BaseModel):
    toolCalls: list[ToolCall]

class VapiRequest(BaseModel):
    message: Message

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Union[str, None]
    completed: bool

    class Config:
        from_attributes = True

class ReminderResponse(BaseModel):
    id: int
    reminder_text: str
    importance: str

    class Config:
        from_attributes = True

class CalendarEventResponse(BaseModel):
    id: int
    title: str
    description: Union[str, None]
    event_from: dt.datetime
    event_to: dt.datetime

    class Config:
        from_attributes = True

# --- Helper function to parse request and find tool_call ---
def _get_validated_tool_call(expected_function_name: str) -> ToolCall:
    """
    Parses the Flask request, validates it against VapiRequest,
    and extracts the specified tool_call.
    Aborts with 400 if validation fails or tool_call is not found.
    """
    json_data = request.get_json()
    if not json_data:
        abort(400, description="Invalid JSON payload. Request body must be JSON.")
    
    try:
        vapi_req = VapiRequest(**json_data)
    except PydanticValidationError as e:
        abort(400, description=f"Invalid request format: {e.errors()}")

    for tool_call in vapi_req.message.toolCalls:
        if tool_call.function.name == expected_function_name:
            # Ensure arguments are a dictionary
            if isinstance(tool_call.function.arguments, str):
                try:
                    tool_call.function.arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    abort(400, description=f"Tool call '{expected_function_name}' arguments are not valid JSON.")
            return tool_call
    
    abort(400, description=f"Invalid Request: Tool call '{expected_function_name}' not found.")


# --- Flask Routes ---
@vapi_flask_bp.route('/create_todo', methods=['POST'])
def create_todo():
    """
    Creates a new Todo item from the provided request data and stores it in the database.
    """
    tool_call = _get_validated_tool_call('createTodo')
    args = tool_call.function.arguments

    title = args.get('title', '')
    description = args.get('description', '')

    # with get_db_session() as db:
    #     todo = Todo(title=title, description=description)
    #     db.add(todo)
    #     db.commit()
    #     db.refresh(todo)
    todo = Todo(title=title, description=description)
    db.session.add(todo)
    db.session.commit()
    db.session.refresh(todo)

    return jsonify({
        'results': [
            {
                'toolCallId': tool_call.id,
                'result': 'success'
            }
        ]
    })

@vapi_flask_bp.route('/get_todos', methods=['POST'])
def get_todos():
    tool_call = _get_validated_tool_call('getTodos')
    
    # with get_db_session() as db:
    #     todos_db = db.query(Todo).all()
    #     todos_response = [TodoResponse.from_orm(todo).dict() for todo in todos_db]
    todos_db = db.session.query(Todo).all()
    todos_response = [TodoResponse.from_orm(todo).dict() for todo in todos_db]

    return jsonify({
        'results': [
            {
                'toolCallId': tool_call.id,
                'result': todos_response
            }
        ]
    })

@vapi_flask_bp.route('/complete_todo', methods=['POST'])
def complete_todo():
    tool_call = _get_validated_tool_call('completeTodo')
    args = tool_call.function.arguments
    
    todo_id = args.get('id')
    if not todo_id:
        abort(400, description='Missing To-Do ID in arguments.')

    # with get_db_session() as db:
    #     todo = db.query(Todo).filter(Todo.id == todo_id).first()
    #     if not todo:
    #         abort(404, description='Todo not found.')
        
    #     todo.completed = True
    #     db.commit()
    #     db.refresh(todo)
    todo = db.session.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        abort(404, description='Todo not found.')
    
    todo.completed = True
    db.session.commit()
    # db.session.refresh(todo) # Refresh might not be strictly necessary if only returning 'success'

    return jsonify({
        'results': [
            {
                'toolCallId': tool_call.id,
                'result': 'success'
            }
        ]
    })

@vapi_flask_bp.route('/delete_todo', methods=['POST'])
def delete_todo():
    tool_call = _get_validated_tool_call('deleteTodo')
    args = tool_call.function.arguments

    todo_id = args.get('id')
    if not todo_id:
        abort(400, description='Missing To-Do ID in arguments.')

    # with get_db_session() as db:
    #     todo = db.query(Todo).filter(Todo.id == todo_id).first()
    #     if not todo:
    #         abort(404, description='Todo not found.')
        
    #     db.delete(todo)
    #     db.commit()
    todo = db.session.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        abort(404, description='Todo not found.')
    
    db.session.delete(todo)
    db.session.commit()

    return jsonify({
        'results': [
            {
                'toolCallId': tool_call.id,
                'result': 'success'
            }
        ]
    })

@vapi_flask_bp.route('/add_reminder', methods=['POST'])
def add_reminder():
    tool_call = _get_validated_tool_call('addReminder')
    args = tool_call.function.arguments

    reminder_text = args.get('reminder_text')
    importance = args.get('importance')

    if not reminder_text or not importance:
        abort(400, description="Missing required fields 'reminder_text' or 'importance' in arguments.")

    # with get_db_session() as db:
    #     reminder = Reminder(reminder_text=reminder_text, importance=importance)
    #     db.add(reminder)
    #     db.commit()
    #     db.refresh(reminder)
    #     response_data = ReminderResponse.from_orm(reminder).dict()
    reminder = Reminder(reminder_text=reminder_text, importance=importance)
    db.session.add(reminder)
    db.session.commit()
    db.session.refresh(reminder)
    response_data = ReminderResponse.from_orm(reminder).dict()

    return jsonify({
        'results': [{
            'toolCallId': tool_call.id,
            'result': response_data
        }]
    })

@vapi_flask_bp.route('/get_reminders', methods=['POST'])
def get_reminders():
    tool_call = _get_validated_tool_call('getReminders')

    # with get_db_session() as db:
    #     reminders_db = db.query(Reminder).all()
    #     reminders_response = [ReminderResponse.from_orm(r).dict() for r in reminders_db]
    reminders_db = db.session.query(Reminder).all()
    reminders_response = [ReminderResponse.from_orm(r).dict() for r in reminders_db]

    return jsonify({
        'results': [{
            'toolCallId': tool_call.id,
            'result': reminders_response
        }]
    })

@vapi_flask_bp.route('/delete_reminder', methods=['POST'])
def delete_reminder():
    tool_call = _get_validated_tool_call('deleteReminder')
    args = tool_call.function.arguments
    
    reminder_id = args.get('id')
    if not reminder_id:
        abort(400, description="Missing reminder ID in arguments.")

    # with get_db_session() as db:
    #     reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    #     if not reminder:
    #         abort(404, description="Reminder not found.")
        
    #     db.delete(reminder)
    #     db.commit()
    reminder = db.session.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        abort(404, description="Reminder not found.")
    
    db.session.delete(reminder)
    db.session.commit()

    return jsonify({
        'results': [{
            'toolCallId': tool_call.id,
            'result': {'id': reminder_id, 'deleted': True}
        }]
    })

@vapi_flask_bp.route('/add_calendar_entry', methods=['POST'])
def add_calendar_entry():
    tool_call = _get_validated_tool_call('addCalendarEntry')
    args = tool_call.function.arguments

    title = args.get('title', '')
    description = args.get('description', '')
    event_from_str = args.get('event_from')
    event_to_str = args.get('event_to')
    
    if not title or not event_from_str or not event_to_str:
        abort(400, description="Missing required fields ('title', 'event_from', 'event_to') in arguments.")
    
    try:
        event_from = dt.datetime.fromisoformat(event_from_str)
        event_to = dt.datetime.fromisoformat(event_to_str)
    except ValueError:
        abort(400, description="Invalid date format for 'event_from' or 'event_to'. Use ISO format (YYYY-MM-DDTHH:MM:SS).")
    
    # with get_db_session() as db:
    #     calendar_event = CalendarEvent(
    #         title=title,
    #         description=description,
    #         event_from=event_from,
    #         event_to=event_to
    #     )
    #     db.add(calendar_event)
    #     db.commit()
    #     db.refresh(calendar_event)
    #     response_data = CalendarEventResponse.from_orm(calendar_event).dict()


    # return jsonify({
    #     'results': [{
    #         'toolCallId': tool_call.id,
    #         'result': response_data
    #     }]
    # })
    calendar_event = CalendarEvent(
        title=title,
        description=description,
        event_from=event_from,
        event_to=event_to
    )
    db.session.add(calendar_event)
    db.session.commit()
    db.session.refresh(calendar_event)
    response_data = CalendarEventResponse.from_orm(calendar_event).dict()

    return jsonify({
        'results': [{
            'toolCallId': tool_call.id,
            'result': response_data
        }]
    })

@vapi_flask_bp.route('/get_calendar_entries', methods=['POST'])
def get_calendar_entries():
    tool_call = _get_validated_tool_call('getCalendarEntries')

    # with get_db_session() as db:
    #     events_db = db.query(CalendarEvent).all()
    #     events_response = [CalendarEventResponse.from_orm(e).dict() for e in events_db]
    events_db = db.session.query(CalendarEvent).all()
    events_response = [CalendarEventResponse.from_orm(e).dict() for e in events_db]
    
    return jsonify({
        'results': [{
            'toolCallId': tool_call.id,
            'result': events_response
        }]
    })


@vapi_flask_bp.route('/delete_calendar_entry', methods=['POST'])
def delete_calendar_entry():
    tool_call = _get_validated_tool_call('deleteCalendarEntry')
    args = tool_call.function.arguments

    event_id = args.get('id')
    if not event_id:
        abort(400, description="Missing event ID in arguments.")

    # with get_db_session() as db:
    #     event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    #     if not event:
    #         abort(404, description="Calendar event not found.")
        
    #     db.delete(event)
    #     db.commit()

    # return jsonify({
    #     'results': [{
    #         'toolCallId': tool_call.id,
    #         'result': {'id': event_id, 'deleted': True}
    #     }]
    # })
    event = db.session.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        abort(404, description="Calendar event not found.")
    
    db.session.delete(event)
    db.session.commit()

    return jsonify({
        'results': [{
            'toolCallId': tool_call.id,
            'result': {'id': event_id, 'deleted': True}
        }]
    })
