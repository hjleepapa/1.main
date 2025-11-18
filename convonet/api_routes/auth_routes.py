"""
Authentication and User Management Routes
Handles user registration, login, and profile management
"""

from flask import Blueprint, request, jsonify
from convonet.security.auth import jwt_auth
from convonet.models.user_models import User, Team, TeamMembership, UserRole, TeamRole
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

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        with SessionLocal() as session:
            existing_user = session.query(User).filter(
                (User.email == data['email']) | (User.username == data['username'])
            ).first()
            
            if existing_user:
                return jsonify({'error': 'User with this email or username already exists'}), 409
            
            # Create new user
            password_hash = jwt_auth.hash_password(data['password'])
            
            user = User(
                email=data['email'],
                username=data['username'],
                password_hash=password_hash,
                first_name=data['first_name'],
                last_name=data['last_name'],
                voice_pin=data.get('voice_pin'),  # Optional PIN for voice authentication
                is_active=True,
                is_verified=False  # In production, implement email verification
            )
            
            session.add(user)
            session.commit()
            session.refresh(user)
            
            # Create access and refresh tokens
            access_token = jwt_auth.create_access_token(
                user_id=str(user.id),
                email=user.email,
                roles=['user']
            )
            refresh_token = jwt_auth.create_refresh_token(str(user.id))
            
            return jsonify({
                'message': 'User registered successfully',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active
                },
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            }), 201
            
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return tokens"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        with SessionLocal() as session:
            user = session.query(User).filter(User.email == data['email']).first()
            
            if not user or not jwt_auth.verify_password(data['password'], user.password_hash):
                return jsonify({'error': 'Invalid email or password'}), 401
            
            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 401
            
            # Update last login
            user.last_login_at = datetime.now(timezone.utc)
            session.commit()
            
            # Get user's team memberships
            team_memberships = session.query(TeamMembership).filter(
                TeamMembership.user_id == user.id
            ).all()
            
            # Create tokens
            access_token = jwt_auth.create_access_token(
                user_id=str(user.id),
                email=user.email,
                roles=['user'],
                team_id=str(team_memberships[0].team_id) if team_memberships else None
            )
            refresh_token = jwt_auth.create_refresh_token(str(user.id))
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name,
                    'is_active': user.is_active,
                    'teams': [
                        {
                            'team_id': str(membership.team_id),
                            'role': (membership.role.value if hasattr(membership.role, 'value') 
                                   else str(membership.role) if isinstance(membership.role, str)
                                   else 'member')
                        }
                        for membership in team_memberships
                    ]
                },
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token is required'}), 400
        
        payload = jwt_auth.verify_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return jsonify({'error': 'Invalid refresh token'}), 401
        
        with SessionLocal() as session:
            user = session.query(User).filter(User.id == payload['user_id']).first()
            
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            # Get user's team memberships
            team_memberships = session.query(TeamMembership).filter(
                TeamMembership.user_id == user.id
            ).all()
            
            # Create new access token
            access_token = jwt_auth.create_access_token(
                user_id=str(user.id),
                email=user.email,
                roles=['user'],
                team_id=str(team_memberships[0].team_id) if team_memberships else None
            )
            
            return jsonify({
                'access_token': access_token
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_auth.require_auth
def get_profile():
    """Get current user profile"""
    try:
        user_id = request.current_user['user_id']
        
        with SessionLocal() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Get team memberships
            team_memberships = session.query(TeamMembership).filter(
                TeamMembership.user_id == user.id
            ).all()
            
            return jsonify({
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name,
                    'is_active': user.is_active,
                    'is_verified': user.is_verified,
                    'created_at': user.created_at.isoformat(),
                    'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
                    'teams': [
                        {
                            'team_id': str(membership.team_id),
                            'role': membership.role.value,
                            'joined_at': membership.joined_at.isoformat()
                        }
                        for membership in team_memberships
                    ]
                }
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_auth.require_auth
def update_profile():
    """Update current user profile"""
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        with SessionLocal() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Update allowed fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'username' in data:
                # Check if username is already taken
                existing_user = session.query(User).filter(
                    User.username == data['username'],
                    User.id != user_id
                ).first()
                if existing_user:
                    return jsonify({'error': 'Username already taken'}), 409
                user.username = data['username']
            
            session.commit()
            
            return jsonify({
                'message': 'Profile updated successfully',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name
                }
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500
