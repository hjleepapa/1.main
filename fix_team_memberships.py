#!/usr/bin/env python3
"""
Fix team memberships - Add admin user to existing teams
This script will be run on the production server to fix the team membership issue
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def main():
    # Database setup - use production DB_URI
    db_uri = os.getenv("DB_URI")
    if not db_uri:
        print("❌ DB_URI environment variable not set")
        print("💡 This script should be run on the production server")
        return
    
    print(f"🔧 Using database: {db_uri.split('@')[1] if '@' in db_uri else 'local'}")
    
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
        
        # Check existing memberships
        result = session.execute(text("SELECT team_id, user_id, role FROM team_memberships_convonet"))
        memberships = result.fetchall()
        print(f"\n🔗 Found {len(memberships)} existing team memberships:")
        for membership in memberships:
            print(f"  - User {membership.user_id} -> Team {membership.team_id} (Role: {membership.role})")
        
        # Find admin user
        result = session.execute(text("SELECT id, email FROM users_convonet WHERE email = 'admin@convonet.com'"))
        admin_user = result.fetchone()
        if not admin_user:
            print("\n❌ Admin user not found!")
            print("💡 Make sure to run the migration script first")
            return
        
        print(f"\n✅ Found admin user: {admin_user.email} (ID: {admin_user.id})")
        
        # Add admin to all existing teams as owner if not already a member
        added_count = 0
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
                    "role": "owner"
                })
                added_count += 1
            else:
                print(f"✅ Admin already member of: {team.name}")
        
        session.commit()
        print(f"\n🎉 Database updated successfully! Added admin to {added_count} teams.")
        
        # Verify final state
        print("\n📋 Final team memberships for admin:")
        result = session.execute(text("""
            SELECT tm.role, t.name 
            FROM team_memberships_convonet tm
            JOIN teams_convonet t ON tm.team_id = t.id
            WHERE tm.user_id = :user_id
        """), {"user_id": admin_user.id})
        admin_memberships = result.fetchall()
        
        if admin_memberships:
            for membership in admin_memberships:
                print(f"  - {membership.name} (Role: {membership.role})")
        else:
            print("  - No team memberships found")
        
        print("\n🚀 The team dropdown should now work in the dashboard!")

if __name__ == "__main__":
    main()
