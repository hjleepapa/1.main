#!/usr/bin/env python3
"""
Reset user password in users_convonet table
Usage: python reset_user_password.py <email_or_username> <new_password>
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from convonet.security.auth import JWTAuth
from convonet.models.user_models import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

def get_database_url():
    """Get database URL from environment or config"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        # Try to construct from individual components
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'convonet')
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return db_url

def reset_password(email_or_username: str, new_password: str):
    """Reset password for a user"""
    # Initialize database connection
    db_url = get_database_url()
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Find user by email or username
        user = db.query(User).filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()
        
        if not user:
            print(f"❌ User not found: {email_or_username}")
            return False
        
        # Hash the new password
        jwt_auth = JWTAuth()
        password_hash = jwt_auth.hash_password(new_password)
        
        # Update password
        user.password_hash = password_hash
        user.updated_at = datetime.now(timezone.utc)
        
        # Commit changes
        db.commit()
        
        print(f"✅ Password reset successful for user: {user.email} ({user.username})")
        print(f"   User ID: {user.id}")
        print(f"   Full Name: {user.full_name}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error resetting password: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reset_user_password.py <email_or_username> <new_password>")
        print("\nExample:")
        print("  python reset_user_password.py user@example.com MyNewPassword123")
        print("  python reset_user_password.py myusername MyNewPassword123")
        sys.exit(1)
    
    email_or_username = sys.argv[1]
    new_password = sys.argv[2]
    
    if len(new_password) < 8:
        print("⚠️  Warning: Password is less than 8 characters. Consider using a stronger password.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(1)
    
    success = reset_password(email_or_username, new_password)
    sys.exit(0 if success else 1)
