#!/usr/bin/env python3
"""
Script to create additional users for testing and demo purposes
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_users():
    """Create additional users for demo purposes"""
    
    db_uri = os.getenv("DB_URI")
    if not db_uri:
        print("❌ DB_URI environment variable not set")
        return False
    
    try:
        print("🔄 Creating additional users...")
        
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from convonet.models.user_models import User, Team, TeamMembership, TeamRole
        from convonet.security.auth import JWTAuth
        
        # Create engine and session
        engine = create_engine(db_uri)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        jwt_auth = JWTAuth()
        
        with SessionLocal() as session:
            # Demo users to create
            demo_users = [
                {
                    'email': 'manager@convonet.com',
                    'username': 'manager',
                    'first_name': 'Project',
                    'last_name': 'Manager',
                    'password': 'manager123'
                },
                {
                    'email': 'developer@convonet.com', 
                    'username': 'developer',
                    'first_name': 'Dev',
                    'last_name': 'Developer',
                    'password': 'dev123'
                },
                {
                    'email': 'designer@convonet.com',
                    'username': 'designer', 
                    'first_name': 'UI',
                    'last_name': 'Designer',
                    'password': 'design123'
                },
                {
                    'email': 'tester@convonet.com',
                    'username': 'tester',
                    'first_name': 'QA',
                    'last_name': 'Tester', 
                    'password': 'test123'
                }
            ]
            
            created_users = []
            
            for user_data in demo_users:
                # Check if user already exists
                existing_user = session.query(User).filter(
                    (User.email == user_data['email']) | (User.username == user_data['username'])
                ).first()
                
                if existing_user:
                    print(f"✅ User already exists: {user_data['email']}")
                    created_users.append(existing_user)
                    continue
                
                # Create new user
                password_hash = jwt_auth.hash_password(user_data['password'])
                
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    password_hash=password_hash,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_active=True,
                    is_verified=True
                )
                
                session.add(user)
                session.commit()
                session.refresh(user)
                
                created_users.append(user)
                print(f"✅ Created user: {user_data['email']}")
            
            # Get or create demo team
            demo_team = session.query(Team).filter(Team.name == 'Demo Team').first()
            
            if demo_team:
                print(f"✅ Using existing demo team: {demo_team.name}")
            else:
                demo_team = Team(
                    name='Demo Team',
                    description='Demo team for testing team collaboration features',
                    is_active=True
                )
                session.add(demo_team)
                session.commit()
                session.refresh(demo_team)
                print(f"✅ Created demo team: {demo_team.name}")
            
            # Add users to demo team
            roles = [TeamRole.ADMIN, TeamRole.MEMBER, TeamRole.MEMBER, TeamRole.VIEWER]
            
            for i, user in enumerate(created_users):
                # Check if user is already a member
                existing_membership = session.query(TeamMembership).filter(
                    TeamMembership.team_id == demo_team.id,
                    TeamMembership.user_id == user.id
                ).first()
                
                if existing_membership:
                    print(f"✅ User {user.email} is already a team member")
                    continue
                
                # Add user to team
                membership = TeamMembership(
                    team_id=demo_team.id,
                    user_id=user.id,
                    role=roles[i] if i < len(roles) else TeamRole.MEMBER
                )
                session.add(membership)
                session.commit()
                
                print(f"✅ Added {user.email} to demo team as {roles[i].value}")
        
        print("\n🎉 User creation completed successfully!")
        print("\n📋 Demo User Credentials:")
        print("=" * 50)
        for user_data in demo_users:
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print(f"Role: {roles[demo_users.index(user_data)].value if demo_users.index(user_data) < len(roles) else 'member'}")
            print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ User creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_users()
    if not success:
        sys.exit(1)
