"""
JWT Authentication System for Convonet
Handles user authentication, token generation, and validation
"""

import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify, current_app
import os

try:
    from convonet.integrations.frontegg_client import frontegg_auth_manager
except Exception:  # pragma: no cover - optional integration
    frontegg_auth_manager = None

class JWTAuth:
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-in-production')
        self.algorithm = 'HS256'
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        self.frontegg_manager = frontegg_auth_manager
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_access_token(self, user_id: str, email: str, roles: list = None, team_id: str = None) -> str:
        """Create a JWT access token"""
        if roles is None:
            roles = ['user']
        
        payload = {
            'user_id': user_id,
            'email': email,
            'roles': roles,
            'team_id': team_id,
            'type': 'access',
            'exp': datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes),
            'iat': datetime.now(timezone.utc)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create a JWT refresh token"""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days),
            'iat': datetime.now(timezone.utc)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        if self.frontegg_manager:
            payload = self.frontegg_manager.verify_token(token)
            if payload:
                return payload
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_token_from_header(self) -> Optional[str]:
        """Extract token from Authorization header"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None
    
    def require_auth(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = self.get_token_from_header()
            
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            payload = self.verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            if payload.get('_provider') == 'frontegg' and self.frontegg_manager:
                request.current_user = self.frontegg_manager.build_request_user(payload)
            else:
                if payload.get('type') != 'access':
                    return jsonify({'error': 'Invalid token type'}), 401
                # Add user info to request context
                request.current_user = {
                    'user_id': payload['user_id'],
                    'email': payload['email'],
                    'roles': payload.get('roles', []),
                    'team_id': payload.get('team_id')
                }
            
            return f(*args, **kwargs)
        return decorated_function
    
    def require_role(self, *required_roles):
        """Decorator to require specific roles"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(request, 'current_user'):
                    return jsonify({'error': 'Authentication required'}), 401
                
                user_roles = request.current_user.get('roles', [])
                if not any(role in user_roles for role in required_roles):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def require_team_member(self, f):
        """Decorator to require team membership"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_team_id = request.current_user.get('team_id')
            if not user_team_id:
                return jsonify({'error': 'Team membership required'}), 403
            
            return f(*args, **kwargs)
        return decorated_function

# Global JWT auth instance
jwt_auth = JWTAuth()

# Convenience decorators
def require_auth(f):
    return jwt_auth.require_auth(f)

def require_role(*roles):
    return jwt_auth.require_role(*roles)

def require_team_member(f):
    return jwt_auth.require_team_member(f)
