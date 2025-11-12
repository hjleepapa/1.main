"""
Team Todo Routes
Enhanced todo management with team collaboration features
"""

from flask import Blueprint, request, jsonify
from convonet.security.auth import jwt_auth, require_auth, require_team_member
from convonet.mcps.local_servers.db_todo import DBTodo, Todo, TodoPriority
from convonet.models.user_models import User, Team, TeamMembership, TeamRole
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_
import os
from datetime import datetime, timezone
from uuid import UUID

# Database setup
db_uri = os.getenv("DB_URI")
engine = create_engine(db_uri)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

team_todo_bp = Blueprint('team_todos', __name__, url_prefix='/api/team-todos')

@team_todo_bp.route('/', methods=['POST'])
@require_auth
def create_team_todo():
    """Create a new team todo"""
    try:
        data = request.get_json()
        current_user_id = request.current_user['user_id']
        current_user_team_id = request.current_user.get('team_id')
        
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        with SessionLocal() as session:
            # Set default due date to today if not provided
            due_date = None
            if data.get('due_date'):
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            else:
                due_date = datetime.now(timezone.utc)
            
            # Create todo
            todo = DBTodo(
                title=data['title'],
                description=data.get('description'),
                priority=data.get('priority', 'medium'),
                due_date=due_date,
                creator_id=current_user_id,
                assignee_id=data.get('assignee_id'),
                team_id=data.get('team_id') or current_user_team_id,
                is_private=data.get('is_private', False)
            )
            
            session.add(todo)
            session.commit()
            session.refresh(todo)
            
            # Get creator and assignee info
            creator = session.query(User).filter(User.id == todo.creator_id).first()
            assignee = session.query(User).filter(User.id == todo.assignee_id).first() if todo.assignee_id else None
            team = session.query(Team).filter(Team.id == todo.team_id).first() if todo.team_id else None
            
            return jsonify({
                'message': 'Team todo created successfully',
                'todo': {
                    'id': str(todo.id),
                    'title': todo.title,
                    'description': todo.description,
                    'priority': todo.priority,
                    'due_date': todo.due_date.isoformat() if todo.due_date else None,
                    'completed': todo.completed,
                    'is_private': todo.is_private,
                    'created_at': todo.created_at.isoformat(),
                    'creator': {
                        'id': str(creator.id),
                        'username': creator.username,
                        'full_name': creator.full_name
                    } if creator else None,
                    'assignee': {
                        'id': str(assignee.id),
                        'username': assignee.username,
                        'full_name': assignee.full_name
                    } if assignee else None,
                    'team': {
                        'id': str(team.id),
                        'name': team.name
                    } if team else None,
                    'google_calendar_event_id': todo.google_calendar_event_id
                }
            }), 201
            
    except Exception as e:
        return jsonify({'error': f'Failed to create team todo: {str(e)}'}), 500

@team_todo_bp.route('/', methods=['GET'])
@require_auth
def get_team_todos():
    """Get todos for the current user's team"""
    try:
        current_user_id = request.current_user['user_id']
        current_user_team_id = request.current_user.get('team_id')
        
        # Query parameters
        team_id = request.args.get('team_id', current_user_team_id)
        assignee_id = request.args.get('assignee_id')
        priority = request.args.get('priority')
        completed = request.args.get('completed')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        with SessionLocal() as session:
            # Build query
            query = session.query(DBTodo)
            
            if team_id:
                query = query.filter(DBTodo.team_id == team_id)
            
            if assignee_id:
                query = query.filter(DBTodo.assignee_id == assignee_id)
            
            if priority:
                query = query.filter(DBTodo.priority == priority)
            
            if completed is not None:
                query = query.filter(DBTodo.completed == (completed.lower() == 'true'))
            
            # Only show todos that user has access to
            # (either they created it, are assigned to it, or it's a team todo they can see)
            query = query.filter(
                or_(
                    DBTodo.creator_id == current_user_id,  # User created it
                    DBTodo.assignee_id == current_user_id,  # User is assigned to it
                    and_(
                        DBTodo.team_id == team_id,
                        DBTodo.is_private == False  # Public team todo
                    )
                )
            )
            
            # Order by due date and priority
            query = query.order_by(DBTodo.due_date.asc(), DBTodo.priority.desc())
            
            todos = query.offset(offset).limit(limit).all()
            
            # Format response
            todo_list = []
            for todo in todos:
                creator = session.query(User).filter(User.id == todo.creator_id).first()
                assignee = session.query(User).filter(User.id == todo.assignee_id).first() if todo.assignee_id else None
                team = session.query(Team).filter(Team.id == todo.team_id).first() if todo.team_id else None
                
                todo_list.append({
                    'id': str(todo.id),
                    'title': todo.title,
                    'description': todo.description,
                    'priority': todo.priority,
                    'due_date': todo.due_date.isoformat() if todo.due_date else None,
                    'completed': todo.completed,
                    'is_private': todo.is_private,
                    'created_at': todo.created_at.isoformat(),
                    'updated_at': todo.updated_at.isoformat(),
                    'creator': {
                        'id': str(creator.id),
                        'username': creator.username,
                        'full_name': creator.full_name
                    } if creator else None,
                    'assignee': {
                        'id': str(assignee.id),
                        'username': assignee.username,
                        'full_name': assignee.full_name
                    } if assignee else None,
                    'team': {
                        'id': str(team.id),
                        'name': team.name
                    } if team else None,
                    'google_calendar_event_id': todo.google_calendar_event_id
                })
            
            return jsonify({
                'todos': todo_list,
                'count': len(todo_list),
                'offset': offset,
                'limit': limit
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to get team todos: {str(e)}'}), 500

@team_todo_bp.route('/<todo_id>', methods=['PUT'])
@require_auth
def update_team_todo(todo_id):
    """Update a team todo"""
    try:
        data = request.get_json()
        current_user_id = request.current_user['user_id']
        
        with SessionLocal() as session:
            todo = session.query(DBTodo).filter(DBTodo.id == todo_id).first()
            
            if not todo:
                return jsonify({'error': 'Todo not found'}), 404
            
            # Check permissions
            can_edit = (
                todo.creator_id == current_user_id or  # User created it
                todo.assignee_id == current_user_id or  # User is assigned to it
                (todo.team_id and not todo.is_private)  # Public team todo
            )
            
            if not can_edit:
                return jsonify({'error': 'Insufficient permissions to edit this todo'}), 403
            
            # Update fields
            if 'title' in data:
                todo.title = data['title']
            if 'description' in data:
                todo.description = data['description']
            if 'priority' in data:
                todo.priority = data['priority']
            if 'due_date' in data:
                if data['due_date']:
                    todo.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                else:
                    todo.due_date = None
            if 'completed' in data:
                todo.completed = data['completed']
            if 'assignee_id' in data:
                todo.assignee_id = data['assignee_id']
            if 'is_private' in data:
                todo.is_private = data['is_private']
            
            todo.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(todo)
            
            # Get updated info
            creator = session.query(User).filter(User.id == todo.creator_id).first()
            assignee = session.query(User).filter(User.id == todo.assignee_id).first() if todo.assignee_id else None
            team = session.query(Team).filter(Team.id == todo.team_id).first() if todo.team_id else None
            
            return jsonify({
                'message': 'Todo updated successfully',
                'todo': {
                    'id': str(todo.id),
                    'title': todo.title,
                    'description': todo.description,
                    'priority': todo.priority,
                    'due_date': todo.due_date.isoformat() if todo.due_date else None,
                    'completed': todo.completed,
                    'is_private': todo.is_private,
                    'created_at': todo.created_at.isoformat(),
                    'updated_at': todo.updated_at.isoformat(),
                    'creator': {
                        'id': str(creator.id),
                        'username': creator.username,
                        'full_name': creator.full_name
                    } if creator else None,
                    'assignee': {
                        'id': str(assignee.id),
                        'username': assignee.username,
                        'full_name': assignee.full_name
                    } if assignee else None,
                    'team': {
                        'id': str(team.id),
                        'name': team.name
                    } if team else None,
                    'google_calendar_event_id': todo.google_calendar_event_id
                }
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to update todo: {str(e)}'}), 500

@team_todo_bp.route('/<todo_id>', methods=['DELETE'])
@require_auth
def delete_team_todo(todo_id):
    """Delete a team todo"""
    try:
        current_user_id = request.current_user['user_id']
        
        with SessionLocal() as session:
            todo = session.query(DBTodo).filter(DBTodo.id == todo_id).first()
            
            if not todo:
                return jsonify({'error': 'Todo not found'}), 404
            
            # Check permissions - only creator or team admins can delete
            can_delete = todo.creator_id == current_user_id
            
            if not can_delete and todo.team_id:
                # Check if user is team admin
                membership = session.query(TeamMembership).filter(
                    TeamMembership.team_id == todo.team_id,
                    TeamMembership.user_id == current_user_id,
                    TeamMembership.role.in_([TeamRole.OWNER, TeamRole.ADMIN])
                ).first()
                can_delete = membership is not None
            
            if not can_delete:
                return jsonify({'error': 'Insufficient permissions to delete this todo'}), 403
            
            session.delete(todo)
            session.commit()
            
            return jsonify({'message': 'Todo deleted successfully'}), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to delete todo: {str(e)}'}), 500

@team_todo_bp.route('/assign', methods=['POST'])
@require_auth
def assign_todo():
    """Assign a todo to a team member"""
    try:
        data = request.get_json()
        current_user_id = request.current_user['user_id']
        todo_id = data.get('todo_id')
        assignee_id = data.get('assignee_id')
        
        if not todo_id or not assignee_id:
            return jsonify({'error': 'todo_id and assignee_id are required'}), 400
        
        with SessionLocal() as session:
            todo = session.query(DBTodo).filter(DBTodo.id == todo_id).first()
            
            if not todo:
                return jsonify({'error': 'Todo not found'}), 404
            
            # Check permissions
            can_assign = (
                todo.creator_id == current_user_id or  # User created it
                todo.assignee_id == current_user_id or  # User is currently assigned
                (todo.team_id and not todo.is_private)  # Public team todo
            )
            
            if not can_assign:
                return jsonify({'error': 'Insufficient permissions to assign this todo'}), 403
            
            # Check if assignee is a team member
            if todo.team_id:
                membership = session.query(TeamMembership).filter(
                    TeamMembership.team_id == todo.team_id,
                    TeamMembership.user_id == assignee_id
                ).first()
                
                if not membership:
                    return jsonify({'error': 'User is not a member of this team'}), 403
            
            # Assign todo
            todo.assignee_id = assignee_id
            todo.updated_at = datetime.now(timezone.utc)
            session.commit()
            
            # Get assignee info
            assignee = session.query(User).filter(User.id == assignee_id).first()
            
            return jsonify({
                'message': 'Todo assigned successfully',
                'todo': {
                    'id': str(todo.id),
                    'title': todo.title,
                    'assignee': {
                        'id': str(assignee.id),
                        'username': assignee.username,
                        'full_name': assignee.full_name
                    }
                }
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to assign todo: {str(e)}'}), 500
