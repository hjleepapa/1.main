import os
import markdown2
from flask import Blueprint, request, jsonify, abort, render_template, current_app
from extensions import db
from .models import Todo, Reminder, CalendarEvent
from .schemas import TodoResponse, ReminderResponse, CalendarEventResponse
from .helpers import _get_validated_tool_call

# It's good practice to define template_folder and static_folder if they exist within the blueprint directory.
syfw_todo_bp = Blueprint(
    'syfw_todo',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@syfw_todo_bp.route('/')
def index():
    """Renders the main page for the SYFW To-Do project."""
    # This will look for 'syfw_todo_index.html' inside the 'syfw_todo/templates/' directory.
    return render_template('syfw_todo_index.html')

@syfw_todo_bp.route('/create_todo', methods=['POST'])
def create_todo():
    tool_call = _get_validated_tool_call('createTodo')
    args = tool_call.function.arguments
    title = args.get('title', '')
    description = args.get('description', '')
    todo = Todo(title=title, description=description)
    db.session.add(todo)
    db.session.commit()
    db.session.refresh(todo)
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@syfw_todo_bp.route('/get_todos', methods=['POST'])
def get_todos():
    tool_call = _get_validated_tool_call('getTodos')
    todos_db = db.session.query(Todo).all()
    todos_response = [TodoResponse.from_orm(todo).dict() for todo in todos_db]
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': todos_response}]})

@syfw_todo_bp.route('/complete_todo', methods=['POST'])
def complete_todo():
    tool_call = _get_validated_tool_call('completeTodo')
    args = tool_call.function.arguments
    todo_id = args.get('id')
    if not todo_id:
        abort(400, description='Missing To-Do ID in arguments.')
    todo = db.session.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        abort(404, description='Todo not found.')
    todo.completed = True
    db.session.commit()
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@syfw_todo_bp.route('/delete_todo', methods=['POST'])
def delete_todo():
    tool_call = _get_validated_tool_call('deleteTodo')
    args = tool_call.function.arguments
    todo_id = args.get('id')
    if not todo_id:
        abort(400, description='Missing To-Do ID in arguments.')
    todo = db.session.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        abort(404, description='Todo not found.')
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@syfw_todo_bp.route('/add_reminder', methods=['POST'])
def add_reminder():
    tool_call = _get_validated_tool_call('addReminder')
    args = tool_call.function.arguments
    reminder_text = args.get('reminder_text', '')
    importance = args.get('importance', '')
    reminder = Reminder(reminder_text=reminder_text, importance=importance)
    db.session.add(reminder)
    db.session.commit()
    db.session.refresh(reminder)
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@syfw_todo_bp.route('/get_reminders', methods=['POST'])
def get_reminders():
    tool_call = _get_validated_tool_call('getReminders')
    reminders_db = db.session.query(Reminder).all()
    reminders_response = [ReminderResponse.from_orm(reminder).dict() for reminder in reminders_db]
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': reminders_response}]})

@syfw_todo_bp.route('/delete_reminder', methods=['POST'])
def delete_reminder():
    tool_call = _get_validated_tool_call('deleteReminder')
    args = tool_call.function.arguments
    reminder_id = args.get('id')
    if not reminder_id:
        abort(400, description='Missing Reminder ID in arguments.')
    reminder = db.session.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        abort(404, description='Reminder not found.')
    db.session.delete(reminder)
    db.session.commit()
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@syfw_todo_bp.route('/add_calendar_entry', methods=['POST'])
def add_calendar_entry():
    tool_call = _get_validated_tool_call('addCalendarEntry')
    args = tool_call.function.arguments
    title = args.get('title', '')
    description = args.get('description', '')
    event_from = args.get('event_from')
    event_to = args.get('event_to')
    event = CalendarEvent(title=title, description=description, event_from=event_from, event_to=event_to)
    db.session.add(event)
    db.session.commit()
    db.session.refresh(event)
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@syfw_todo_bp.route('/get_calendar_entries', methods=['POST'])
def get_calendar_entries():
    tool_call = _get_validated_tool_call('getCalendarEntries')
    events_db = db.session.query(CalendarEvent).all()
    events_response = [CalendarEventResponse.from_orm(event).dict() for event in events_db]
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': events_response}]})

@syfw_todo_bp.route('/delete_calendar_entry', methods=['POST'])
def delete_calendar_entry():
    tool_call = _get_validated_tool_call('deleteCalendarEntry')
    args = tool_call.function.arguments
    event_id = args.get('id')
    if not event_id:
        abort(400, description='Missing Calendar Event ID in arguments.')
    event = db.session.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        abort(404, description='Calendar event not found.')
    db.session.delete(event)
    db.session.commit()
    return jsonify({'results': [{'toolCallId': tool_call.id, 'result': 'success'}]})

@syfw_todo_bp.route('/readme')
def view_syfw_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README_syfw_toDoList.md')
    if not os.path.exists(readme_path):
        return 'README not found.'
    with open(readme_path, 'r') as f:
        markdown_content = f.read()
    html_content = markdown2.markdown(markdown_content)
    return render_template('show_markdown.html', content=html_content) 