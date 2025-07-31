import os
import markdown2
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, abort, render_template, current_app
from extensions import db
from .models import VapiTodo, VapiReminder, VapiCalendarEvent # Models are specific, so they stay
from shared.schemas import TodoResponse, ReminderResponse, CalendarEventResponse
from shared.helpers import get_validated_tool_call
from shared.google_calendar import get_calendar_service

vapi_flask_bp = Blueprint(
    'vapi_flask',
    __name__,
    url_prefix='/vapi_project',
    static_folder='static',
    static_url_path='/static'
)

@vapi_flask_bp.route('/create_todo', methods=['POST'])
def create_todo():
    tool_call = get_validated_tool_call('createTodo')
    args = tool_call.function.arguments
    title = args.get('title', '')
    description = args.get('description', '')
    
    # Create todo in database
    todo = VapiTodo(title=title, description=description)
    db.session.add(todo)
    db.session.commit()
    db.session.refresh(todo)
    
    # Sync with Google Calendar
    try:
        calendar_service = get_calendar_service()
        google_event_id = calendar_service.create_event(
            title=f"TODO: {title}",
            description=description or "Task from VAPI Todo System"
        )
        if google_event_id:
            todo.google_calendar_event_id = google_event_id
            db.session.commit()
    except Exception as e:
        print(f"Failed to sync with Google Calendar: {e}")
    
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@vapi_flask_bp.route('/get_todos', methods=['POST'])
def get_todos():
    tool_call = get_validated_tool_call('getTodos')
    todos_db = db.session.query(VapiTodo).all()
    todos_response = [TodoResponse.model_validate(todo).model_dump() for todo in todos_db]
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': todos_response}]})

@vapi_flask_bp.route('/complete_todo', methods=['POST'])
def complete_todo():
    tool_call = get_validated_tool_call('completeTodo')
    args = tool_call.function.arguments
    todo_id = args.get('id')
    if not todo_id:
        abort(400, description='Missing To-Do ID in arguments.')
    
    todo = db.session.query(VapiTodo).filter(VapiTodo.id == todo_id).first()
    if not todo:
        abort(404, description='Todo not found.')
    
    todo.completed = True
    db.session.commit()
    
    # Update Google Calendar event
    if todo.google_calendar_event_id:
        try:
            calendar_service = get_calendar_service()
            calendar_service.update_event(
                event_id=todo.google_calendar_event_id,
                title=f"COMPLETED: {todo.title}",
                description=f"{todo.description or ''}\n\nStatus: Completed"
            )
        except Exception as e:
            print(f"Failed to update Google Calendar event: {e}")
    
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@vapi_flask_bp.route('/delete_todo', methods=['POST'])
def delete_todo():
    tool_call = get_validated_tool_call('deleteTodo')
    args = tool_call.function.arguments
    todo_id = args.get('id')
    if not todo_id:
        abort(400, description='Missing To-Do ID in arguments.')
    
    todo = db.session.query(VapiTodo).filter(VapiTodo.id == todo_id).first()
    if not todo:
        abort(404, description='Todo not found.')
    
    # Delete from Google Calendar first
    if todo.google_calendar_event_id:
        try:
            calendar_service = get_calendar_service()
            calendar_service.delete_event(todo.google_calendar_event_id)
        except Exception as e:
            print(f"Failed to delete Google Calendar event: {e}")
    
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@vapi_flask_bp.route('/add_reminder', methods=['POST'])
def add_reminder():
    tool_call = get_validated_tool_call('addReminder')
    args = tool_call.function.arguments
    reminder_text = args.get('reminder_text', '')
    importance = args.get('importance', '')
    
    # Create reminder in database
    reminder = VapiReminder(reminder_text=reminder_text, importance=importance)
    db.session.add(reminder)
    db.session.commit()
    db.session.refresh(reminder)
    
    # Sync with Google Calendar
    try:
        calendar_service = get_calendar_service()
        google_event_id = calendar_service.create_event(
            title=f"REMINDER: {reminder_text}",
            description=f"Importance: {importance}\nReminder from VAPI Todo System"
        )
        if google_event_id:
            reminder.google_calendar_event_id = google_event_id
            db.session.commit()
    except Exception as e:
        print(f"Failed to sync reminder with Google Calendar: {e}")
    
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@vapi_flask_bp.route('/get_reminders', methods=['POST'])
def get_reminders():
    tool_call = get_validated_tool_call('getReminders')
    reminders_db = db.session.query(VapiReminder).all()
    reminders_response = [ReminderResponse.model_validate(reminder).model_dump() for reminder in reminders_db]
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': reminders_response}]})

@vapi_flask_bp.route('/delete_reminder', methods=['POST'])
def delete_reminder():
    tool_call = get_validated_tool_call('deleteReminder')
    args = tool_call.function.arguments
    reminder_id = args.get('id')
    if not reminder_id:
        abort(400, description='Missing Reminder ID in arguments.')
    
    reminder = db.session.query(VapiReminder).filter(VapiReminder.id == reminder_id).first()
    if not reminder:
        abort(404, description='Reminder not found.')
    
    # Delete from Google Calendar first
    if reminder.google_calendar_event_id:
        try:
            calendar_service = get_calendar_service()
            calendar_service.delete_event(reminder.google_calendar_event_id)
        except Exception as e:
            print(f"Failed to delete Google Calendar event: {e}")
    
    db.session.delete(reminder)
    db.session.commit()
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@vapi_flask_bp.route('/add_calendar_entry', methods=['POST'])
def add_calendar_entry():
    tool_call = get_validated_tool_call('addCalendarEntry')
    args = tool_call.function.arguments
    title = args.get('title', '')
    description = args.get('description', '')
    event_from = args.get('event_from')
    event_to = args.get('event_to')
    
    # Parse datetime strings
    start_time = None
    end_time = None
    if event_from:
        try:
            start_time = datetime.fromisoformat(event_from.replace('Z', '+00:00'))
        except:
            start_time = datetime.utcnow()
    if event_to:
        try:
            end_time = datetime.fromisoformat(event_to.replace('Z', '+00:00'))
        except:
            end_time = start_time + timedelta(hours=1) if start_time else datetime.utcnow() + timedelta(hours=1)
    
    # Create calendar event in database
    event = VapiCalendarEvent(title=title, description=description, event_from=start_time, event_to=end_time)
    db.session.add(event)
    db.session.commit()
    db.session.refresh(event)
    
    # Sync with Google Calendar
    try:
        calendar_service = get_calendar_service()
        google_event_id = calendar_service.create_event(
            title=title,
            description=description or "Event from VAPI Todo System",
            start_time=start_time,
            end_time=end_time
        )
        if google_event_id:
            event.google_calendar_event_id = google_event_id
            db.session.commit()
    except Exception as e:
        print(f"Failed to sync calendar event with Google Calendar: {e}")
    
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@vapi_flask_bp.route('/get_calendar_entries', methods=['POST'])
def get_calendar_entries():
    tool_call = get_validated_tool_call('getCalendarEntries')
    events_db = db.session.query(VapiCalendarEvent).all()
    events_response = [CalendarEventResponse.model_validate(event).model_dump() for event in events_db]
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': events_response}]})

@vapi_flask_bp.route('/delete_calendar_entry', methods=['POST'])
def delete_calendar_entry():
    tool_call = get_validated_tool_call('deleteCalendarEntry')
    args = tool_call.function.arguments
    event_id = args.get('id')
    if not event_id:
        abort(400, description='Missing Calendar Event ID in arguments.')
    
    event = db.session.query(VapiCalendarEvent).filter(VapiCalendarEvent.id == event_id).first()
    if not event:
        abort(404, description='Calendar event not found.')
    
    # Delete from Google Calendar first
    if event.google_calendar_event_id:
        try:
            calendar_service = get_calendar_service()
            calendar_service.delete_event(event.google_calendar_event_id)
        except Exception as e:
            print(f"Failed to delete Google Calendar event: {e}")
    
    db.session.delete(event)
    db.session.commit()
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@vapi_flask_bp.route('/readme')
def view_vapi_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README_VAPI_toDoList.md')
    if not os.path.exists(readme_path):
        return 'README not found.'
    with open(readme_path, 'r') as f:
        markdown_content = f.read()
    html_content = markdown2.markdown(markdown_content)
    return render_template('show_markdown.html', content=html_content) 