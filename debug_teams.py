#!/usr/bin/env python3
"""
Debug script to check teams and add admin user to existing teams
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from enum import Enum

# Define TeamRole enum locally to avoid import issues
class TeamRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

def main():
    # Database setup - try different sources
    db_uri = os.getenv("DB_URI")
    
    if not db_uri:
        # Try to use the same database as the Flask app
        # This assumes you're using PostgreSQL locally
        db_uri = "postgresql://hj:password@localhost/hjlees_db"
        print(f"🔧 Using default database URI: {db_uri}")
    else:
        print(f"🔧 Using DB_URI from environment: {db_uri}")
    
    engine = create_engine(db_uri)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        print("🔍 Checking existing data...")
        
        # Check users
        result = session.execute(text("SELECT id, email, username FROM users_convonet"))
        users = result.fetchall()
        print(f"👥 Found {len(users)} users:")
        for user in users:
            print(f"  - {user.email} (ID: {user.id})")
        
        # Check teams
        result = session.execute(text("SELECT id, name, description FROM teams_convonet"))
        teams = result.fetchall()
        print(f"\n🏢 Found {len(teams)} teams:")
        for team in teams:
            print(f"  - {team.name} (ID: {team.id})")
        
        # Check memberships
        result = session.execute(text("SELECT team_id, user_id, role FROM team_memberships_convonet"))
        memberships = result.fetchall()
        print(f"\n🔗 Found {len(memberships)} team memberships:")
        for membership in memberships:
            print(f"  - User {membership.user_id} -> Team {membership.team_id} (Role: {membership.role})")
        
        # Find admin user
        result = session.execute(text("SELECT id, email FROM users_convonet WHERE email = 'admin@convonet.com'"))
        admin_user = result.fetchone()
        if not admin_user:
            print("\n❌ Admin user not found!")
            return
        
        print(f"\n✅ Found admin user: {admin_user.email} (ID: {admin_user.id})")
        
        # Add admin to all existing teams as owner if not already a member
        for team in teams:
            result = session.execute(text("""
                SELECT id FROM team_memberships_convonet 
                WHERE team_id = :team_id AND user_id = :user_id
            """), {"team_id": team.id, "user_id": admin_user.id})
            existing_membership = result.fetchone()
            
            if not existing_membership:
                print(f"➕ Adding admin to team: {team.name}")
                session.execute(text("""
                    INSERT INTO team_memberships_convonet (team_id, user_id, role, joined_at)
                    VALUES (:team_id, :user_id, :role, NOW())
                """), {
                    "team_id": team.id,
                    "user_id": admin_user.id,
                    "role": TeamRole.OWNER.value
                })
            else:
                print(f"✅ Admin already member of: {team.name}")
        
        session.commit()
        print("\n🎉 Database updated successfully!")
        
        # Verify final state
        print("\n📋 Final team memberships for admin:")
        result = session.execute(text("""
            SELECT tm.role, t.name 
            FROM team_memberships_convonet tm
            JOIN teams_convonet t ON tm.team_id = t.id
            WHERE tm.user_id = :user_id
        """), {"user_id": admin_user.id})
        admin_memberships = result.fetchall()
        
        for membership in admin_memberships:
            print(f"  - {membership.name} (Role: {membership.role})")

if __name__ == "__main__":
    main()
