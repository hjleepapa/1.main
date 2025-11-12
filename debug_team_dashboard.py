"""
Debug team dashboard - check teams and memberships
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from convonet.models.user_models import User, Team, TeamMembership
from dotenv import load_dotenv

load_dotenv()

db_uri = os.getenv("DB_URI", "postgresql://postgres:postgres@localhost:5432/postgres")

print(f"🔧 Connecting to database...")
engine = create_engine(db_uri)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

with SessionLocal() as session:
    # List all teams
    print(f"\n{'='*60}")
    print(f"ALL TEAMS:")
    print(f"{'='*60}")
    teams = session.query(Team).all()
    if teams:
        for team in teams:
            print(f"\n📋 Team: {team.name}")
            print(f"   ID: {team.id}")
            print(f"   Description: {team.description or 'No description'}")
            print(f"   Active: {team.is_active}")
            print(f"   Created: {team.created_at}")
    else:
        print("❌ No teams found")
    
    # List all users
    print(f"\n{'='*60}")
    print(f"ALL USERS:")
    print(f"{'='*60}")
    users = session.query(User).all()
    if users:
        for user in users:
            print(f"\n👤 User: {user.full_name}")
            print(f"   Email: {user.email}")
            print(f"   ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Active: {user.is_active}")
            print(f"   Voice PIN: {user.voice_pin or 'NOT SET'}")
    else:
        print("❌ No users found")
    
    # List all memberships
    print(f"\n{'='*60}")
    print(f"ALL TEAM MEMBERSHIPS:")
    print(f"{'='*60}")
    memberships = session.query(TeamMembership, User, Team).join(
        User, TeamMembership.user_id == User.id
    ).join(
        Team, TeamMembership.team_id == Team.id
    ).all()
    
    if memberships:
        for membership, user, team in memberships:
            print(f"\n🔗 {user.full_name} → {team.name}")
            print(f"   Role: {membership.role.value}")
            print(f"   Joined: {membership.joined_at}")
    else:
        print("❌ No team memberships found")
    
    # Check admin user specifically
    print(f"\n{'='*60}")
    print(f"ADMIN USER CHECK:")
    print(f"{'='*60}")
    admin = session.query(User).filter(User.email == 'admin@convonet.com').first()
    if admin:
        print(f"✅ Admin user found: {admin.full_name}")
        print(f"   ID: {admin.id}")
        print(f"   Email: {admin.email}")
        print(f"   Active: {admin.is_active}")
        print(f"   Voice PIN: {admin.voice_pin or 'NOT SET'}")
        
        # Get admin's teams
        admin_teams = session.query(TeamMembership, Team).join(
            Team, TeamMembership.team_id == Team.id
        ).filter(TeamMembership.user_id == admin.id).all()
        
        if admin_teams:
            print(f"\n   Admin's Teams:")
            for membership, team in admin_teams:
                print(f"   • {team.name} ({membership.role.value})")
        else:
            print(f"\n   ⚠️ Admin is NOT a member of any teams!")
            print(f"   This is why the dropdown is empty!")
    else:
        print(f"❌ Admin user not found")

print(f"\n{'='*60}")
print(f"RECOMMENDATIONS:")
print(f"{'='*60}")

if not memberships:
    print("⚠️ No team memberships exist!")
    print("💡 Create memberships manually or via web dashboard")
elif admin and not admin_teams:
    print("⚠️ Admin user exists but has no team memberships!")
    print("💡 Add admin to teams using:")
    print(f"   python fix_team_memberships.py")
    print(f"   OR add via web dashboard once logged in")

print(f"\n✅ Debug complete!")

