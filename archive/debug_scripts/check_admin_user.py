"""
Check and fix admin user credentials
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Import after loading .env
from convonet.models.user_models import User
from convonet.security.auth import jwt_auth

# Get database URI
db_uri = os.getenv("DB_URI", "postgresql://postgres:postgres@localhost:5432/postgres")

print(f"🔧 Connecting to database...")
engine = create_engine(db_uri)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# First, check if voice_pin column exists
try:
    with engine.connect() as conn:
        check_column_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users_convonet' 
            AND column_name = 'voice_pin'
        """)
        result = conn.execute(check_column_sql).fetchone()
        
        if not result:
            print(f"⚠️  voice_pin column does not exist yet!")
            print(f"🔧 Running migration to add voice_pin column...")
            
            # Add the column
            alter_sql = text("""
                ALTER TABLE users_convonet 
                ADD COLUMN voice_pin VARCHAR(10) UNIQUE
            """)
            conn.execute(alter_sql)
            
            # Create index
            index_sql = text("""
                CREATE INDEX IF NOT EXISTS idx_users_voice_pin 
                ON users_convonet(voice_pin)
            """)
            conn.execute(index_sql)
            
            conn.commit()
            print(f"✅ voice_pin column added successfully!")
except Exception as e:
    print(f"❌ Error checking/adding voice_pin column: {e}")
    print(f"💡 Try running: python run_voice_pin_migration.py")
    exit(1)

with SessionLocal() as session:
    # Check if admin user exists
    admin = session.query(User).filter(User.email == 'admin@convonet.com').first()
    
    if admin:
        print(f"✅ Admin user found:")
        print(f"   Email: {admin.email}")
        print(f"   Username: {admin.username}")
        print(f"   Name: {admin.full_name}")
        print(f"   Active: {admin.is_active}")
        print(f"   Voice PIN: {admin.voice_pin or 'NOT SET'}")
        
        # Test password
        if jwt_auth.verify_password('admin123', admin.password_hash):
            print(f"✅ Password 'admin123' is correct")
        else:
            print(f"❌ Password 'admin123' does NOT match")
            print(f"🔧 Updating password to 'admin123'...")
            admin.password_hash = jwt_auth.hash_password('admin123')
            session.commit()
            print(f"✅ Password updated successfully")
        
        # Set voice PIN if not set
        if not admin.voice_pin:
            print(f"🔧 Setting voice PIN to '1234'...")
            admin.voice_pin = '1234'
            session.commit()
            print(f"✅ Voice PIN set to '1234'")
        
        print(f"\n📋 DEMO CREDENTIALS:")
        print(f"   Web Login: admin@convonet.com / admin123")
        print(f"   Voice PIN: {admin.voice_pin}")
        
    else:
        print(f"❌ Admin user NOT found")
        print(f"🔧 Creating admin user...")
        
        admin = User(
            email='admin@convonet.com',
            username='admin',
            password_hash=jwt_auth.hash_password('admin123'),
            first_name='Admin',
            last_name='User',
            voice_pin='1234',
            is_active=True,
            is_verified=True
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)
        
        print(f"✅ Admin user created:")
        print(f"   Email: admin@convonet.com")
        print(f"   Password: admin123")
        print(f"   Voice PIN: 1234")
        print(f"   User ID: {admin.id}")

print(f"\n✅ Done!")

