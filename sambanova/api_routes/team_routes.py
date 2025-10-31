"""
Team Management Routes
Handles team creation, member management, and team operations
"""

from flask import Blueprint, request, jsonify
from sambanova.security.auth import jwt_auth, require_auth, require_team_member
from sambanova.models.user_models import User, Team, TeamMembership, TeamRole
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime, timezone
from uuid import uuid4

# Database setup
db_uri = os.getenv("DB_URI")
engine = create_engine(db_uri)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

team_bp = Blueprint('teams', __name__, url_prefix='/api/teams')

@team_bp.route('/', methods=['POST'])
@require_auth
def create_team():
    """Create a new team"""
    try:
        data = request.get_json()
        user_id = request.current_user['user_id']
        
        if not data.get('name'):
            return jsonify({'error': 'Team name is required'}), 400
        
        with SessionLocal() as session:
            # Create team
            team = Team(
                name=data['name'],
                description=data.get('description', ''),
                is_active=True
            )
            session.add(team)
            session.commit()
            session.refresh(team)
            
            # Add creator as team owner
            membership = TeamMembership(
                team_id=team.id,
                user_id=user_id,
                role=TeamRole.OWNER
            )
            session.add(membership)
            session.commit()
            
            return jsonify({
                'message': 'Team created successfully',
                'team': {
                    'id': str(team.id),
                    'name': team.name,
                    'description': team.description,
                    'created_at': team.created_at.isoformat(),
                    'members_count': 1
                }
            }), 201
            
    except Exception as e:
        return jsonify({'error': f'Failed to create team: {str(e)}'}), 500

@team_bp.route('/', methods=['GET'])
@require_auth
def get_user_teams():
    """Get all teams for the current user"""
    try:
        user_id = request.current_user['user_id']
        
        with SessionLocal() as session:
            # Use join query instead of relationship to avoid issues
            results = session.query(TeamMembership, Team).join(
                Team, TeamMembership.team_id == Team.id
            ).filter(
                TeamMembership.user_id == user_id
            ).all()
            
            teams = []
            for membership, team in results:
                # Handle role value - could be enum or string
                role_value = membership.role.value if hasattr(membership.role, 'value') else str(membership.role).lower()
                
                teams.append({
                    'id': str(team.id),
                    'name': team.name,
                    'description': team.description,
                    'role': role_value,
                    'joined_at': membership.joined_at.isoformat(),
                    'created_at': team.created_at.isoformat(),
                    'is_active': team.is_active
                })
            
            return jsonify({'teams': teams}), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to get teams: {str(e)}'}), 500

@team_bp.route('/<team_id>', methods=['GET'])
@require_auth
@require_team_member
def get_team(team_id):
    """Get team details and members"""
    try:
        with SessionLocal() as session:
            team = session.query(Team).filter(Team.id == team_id).first()
            
            if not team:
                return jsonify({'error': 'Team not found'}), 404
            
            # Get team members using join query
            member_results = session.query(TeamMembership, User).join(
                User, TeamMembership.user_id == User.id
            ).filter(
                TeamMembership.team_id == team_id
            ).all()
            
            members = []
            for membership, user in member_results:
                # Handle role value - could be enum or string
                role_value = membership.role.value if hasattr(membership.role, 'value') else str(membership.role).lower()
                
                members.append({
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name,
                    'role': role_value,
                    'joined_at': membership.joined_at.isoformat()
                })
            
            return jsonify({
                'team': {
                    'id': str(team.id),
                    'name': team.name,
                    'description': team.description,
                    'created_at': team.created_at.isoformat(),
                    'is_active': team.is_active,
                    'members': members,
                    'members_count': len(members)
                }
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to get team: {str(e)}'}), 500

@team_bp.route('/<team_id>/members', methods=['POST'])
@require_auth
@require_team_member
def add_team_member(team_id):
    """Add a member to the team"""
    try:
        data = request.get_json()
        current_user_id = request.current_user['user_id']
        
        if not data.get('user_id') or not data.get('role'):
            return jsonify({'error': 'user_id and role are required'}), 400
        
        with SessionLocal() as session:
            # Get current user to check if they're the admin user
            current_user = session.query(User).filter(User.id == current_user_id).first()
            is_admin_user = current_user and current_user.email == 'admin@sambanova.com'
            
            # Check if current user has permission to add members
            # Admin user can add members to any team, otherwise must be team OWNER/ADMIN
            if not is_admin_user:
                current_membership = session.query(TeamMembership).filter(
                    TeamMembership.team_id == team_id,
                    TeamMembership.user_id == current_user_id
                ).first()
                
                if not current_membership or current_membership.role not in [TeamRole.OWNER, TeamRole.ADMIN]:
                    return jsonify({'error': 'Insufficient permissions to add members'}), 403
            
            # Check if user exists
            user = session.query(User).filter(User.id == data['user_id']).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Check if user is already a member
            existing_membership = session.query(TeamMembership).filter(
                TeamMembership.team_id == team_id,
                TeamMembership.user_id == data['user_id']
            ).first()
            
            if existing_membership:
                return jsonify({'error': 'User is already a team member'}), 409
            
            # Add member
            membership = TeamMembership(
                team_id=team_id,
                user_id=data['user_id'],
                role=TeamRole(data['role'])
            )
            session.add(membership)
            session.commit()
            
            return jsonify({
                'message': 'Member added successfully',
                'member': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': membership.role.value if hasattr(membership.role, 'value') else str(membership.role).lower(),
                    'joined_at': membership.joined_at.isoformat()
                }
            }), 201
            
    except ValueError:
        return jsonify({'error': 'Invalid role'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to add member: {str(e)}'}), 500

@team_bp.route('/<team_id>/members/<user_id>', methods=['DELETE'])
@require_auth
@require_team_member
def remove_team_member(team_id, user_id):
    """Remove a member from the team"""
    try:
        current_user_id = request.current_user['user_id']
        
        with SessionLocal() as session:
            # Get current user to check if they're the admin user
            current_user = session.query(User).filter(User.id == current_user_id).first()
            is_admin_user = current_user and current_user.email == 'admin@sambanova.com'
            
            # Check if current user has permission to remove members
            # Admin user can remove members from any team, otherwise must be team OWNER/ADMIN
            if not is_admin_user:
                current_membership = session.query(TeamMembership).filter(
                    TeamMembership.team_id == team_id,
                    TeamMembership.user_id == current_user_id
                ).first()
                
                if not current_membership or current_membership.role not in [TeamRole.OWNER, TeamRole.ADMIN]:
                    return jsonify({'error': 'Insufficient permissions to remove members'}), 403
            
            # Check if user is trying to remove themselves
            if user_id == current_user_id:
                return jsonify({'error': 'Cannot remove yourself from the team'}), 400
            
            # Remove membership
            membership = session.query(TeamMembership).filter(
                TeamMembership.team_id == team_id,
                TeamMembership.user_id == user_id
            ).first()
            
            if not membership:
                return jsonify({'error': 'Member not found'}), 404
            
            session.delete(membership)
            session.commit()
            
            return jsonify({'message': 'Member removed successfully'}), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to remove member: {str(e)}'}), 500

@team_bp.route('/<team_id>/members/<user_id>/role', methods=['PUT'])
@require_auth
@require_team_member
def update_member_role(team_id, user_id):
    """Update a member's role in the team"""
    try:
        data = request.get_json()
        current_user_id = request.current_user['user_id']
        
        if not data.get('role'):
            return jsonify({'error': 'role is required'}), 400
        
        with SessionLocal() as session:
            # Check if current user has permission to update roles
            current_membership = session.query(TeamMembership).filter(
                TeamMembership.team_id == team_id,
                TeamMembership.user_id == current_user_id
            ).first()
            
            if not current_membership or current_membership.role != TeamRole.OWNER:
                return jsonify({'error': 'Only team owners can update member roles'}), 403
            
            # Update membership role
            membership = session.query(TeamMembership).filter(
                TeamMembership.team_id == team_id,
                TeamMembership.user_id == user_id
            ).first()
            
            if not membership:
                return jsonify({'error': 'Member not found'}), 404
            
            membership.role = TeamRole(data['role'])
            session.commit()
            
            return jsonify({
                'message': 'Member role updated successfully',
                'member': {
                    'id': str(user_id),
                    'role': membership.role.value if hasattr(membership.role, 'value') else str(membership.role).lower()
                }
            }), 200
            
    except ValueError:
        return jsonify({'error': 'Invalid role'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update member role: {str(e)}'}), 500

@team_bp.route('/search/users', methods=['GET'])
@require_auth
def search_users():
    """Search for users to add to teams"""
    try:
        query = request.args.get('q', '')
        
        if len(query) < 2:
            return jsonify({'error': 'Query must be at least 2 characters'}), 400
        
        with SessionLocal() as session:
            users = session.query(User).filter(
                User.is_active == True,
                (User.username.ilike(f'%{query}%')) | 
                (User.email.ilike(f'%{query}%')) |
                (User.first_name.ilike(f'%{query}%')) |
                (User.last_name.ilike(f'%{query}%'))
            ).limit(10).all()
            
            results = []
            for user in users:
                results.append({
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name
                })
            
            return jsonify({'users': results}), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to search users: {str(e)}'}), 500
