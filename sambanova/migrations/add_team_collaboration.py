"""
Database migration to add team collaboration features
Adds users, teams, and team_memberships tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sambanova.models.user_models import User, Team, TeamMembership, UserRole, TeamRole

def run_migration():
    """Run the migration to create team collaboration tables"""
    
    db_uri = os.getenv("DB_URI")
    if not db_uri:
        print("❌ DB_URI environment variable not set")
        return False
    
    print(f"🔧 Using database URI: {db_uri[:20]}...")
    
    try:
        print("🔄 Starting team collaboration migration...")
        
        # Create engine
        engine = create_engine(db_uri)
        
        # Create tables
        print("🔧 Creating user and team tables...")
        
        # Create users table
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users_sambanova (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE NOT NULL,
                    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    last_login_at TIMESTAMP WITH TIME ZONE
                );
            """))
            
            # Create indexes for users
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users_sambanova(email);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_username ON users_sambanova(username);"))
            
            # Create teams table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS teams_sambanova (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
                );
            """))
            
            # Create team_memberships table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS team_memberships_sambanova (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    team_id UUID NOT NULL REFERENCES teams_sambanova(id),
                    user_id UUID NOT NULL REFERENCES users_sambanova(id),
                    role VARCHAR(20) DEFAULT 'member' NOT NULL,
                    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    UNIQUE(team_id, user_id)
                );
            """))
            
            # Create indexes for team_memberships
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_team_memberships_team_id ON team_memberships_sambanova(team_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_team_memberships_user_id ON team_memberships_sambanova(user_id);"))
            conn.commit()
        
        # Add team collaboration columns to existing todos table
        print("🔧 Adding team collaboration columns to todos table...")
        
        # Check if columns already exist before adding them
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'todos_sambanova' 
                AND column_name IN ('creator_id', 'assignee_id', 'team_id', 'is_private');
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'creator_id' not in existing_columns:
                conn.execute(text("ALTER TABLE todos_sambanova ADD COLUMN creator_id UUID;"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_todos_creator_id ON todos_sambanova(creator_id);"))
            
            if 'assignee_id' not in existing_columns:
                conn.execute(text("ALTER TABLE todos_sambanova ADD COLUMN assignee_id UUID;"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_todos_assignee_id ON todos_sambanova(assignee_id);"))
            
            if 'team_id' not in existing_columns:
                conn.execute(text("ALTER TABLE todos_sambanova ADD COLUMN team_id UUID;"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_todos_team_id ON todos_sambanova(team_id);"))
            
            if 'is_private' not in existing_columns:
                conn.execute(text("ALTER TABLE todos_sambanova ADD COLUMN is_private BOOLEAN DEFAULT FALSE NOT NULL;"))
            
            conn.commit()
        
        # Create a sample admin user and team for testing
        print("🔧 Creating sample admin user and team...")
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        with SessionLocal() as session:
            # Check if admin user already exists
            admin_user = session.query(User).filter(User.email == 'admin@sambanova.com').first()
            
            if not admin_user:
                # Create admin user
                from sambanova.security.auth import JWTAuth
                jwt_auth = JWTAuth()
                
                admin_user = User(
                    email='admin@sambanova.com',
                    username='admin',
                    password_hash=jwt_auth.hash_password('admin123'),
                    first_name='Admin',
                    last_name='User',
                    is_active=True,
                    is_verified=True
                )
                session.add(admin_user)
                session.commit()
                session.refresh(admin_user)
                
                print(f"✅ Created admin user: {admin_user.email}")
            else:
                print(f"✅ Admin user already exists: {admin_user.email}")
            
            # Check if demo team already exists
            demo_team = session.query(Team).filter(Team.name == 'Demo Team').first()
            
            if not demo_team:
                # Create demo team
                demo_team = Team(
                    name='Demo Team',
                    description='Demo team for testing team collaboration features',
                    is_active=True
                )
                session.add(demo_team)
                session.commit()
                session.refresh(demo_team)
                
                print(f"✅ Created demo team: {demo_team.name}")
            else:
                print(f"✅ Demo team already exists: {demo_team.name}")
            
            # Check if admin is already a member of demo team
            membership = session.query(TeamMembership).filter(
                TeamMembership.team_id == demo_team.id,
                TeamMembership.user_id == admin_user.id
            ).first()
            
            if not membership:
                # Add admin as team owner
                membership = TeamMembership(
                    team_id=demo_team.id,
                    user_id=admin_user.id,
                    role=TeamRole.OWNER
                )
                session.add(membership)
                session.commit()
                
                print(f"✅ Added admin as owner of demo team")
            else:
                print(f"✅ Admin is already a member of demo team")
        
        print("✅ Team collaboration migration completed successfully!")
        print("\n📋 Sample credentials:")
        print("Email: admin@sambanova.com")
        print("Password: admin123")
        print("Team: Demo Team")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\n🎉 Migration completed successfully!")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)
