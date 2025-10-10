"""
Check and fix admin user credentials
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sambanova.models.user_models import User
from sambanova.security.auth import jwt_auth

# Get database URI
db_uri = os.getenv("DB_URI", "postgresql://postgres:postgres@localhost:5432/postgres")

print(f"🔧 Connecting to database...")
engine = create_engine(db_uri)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

with SessionLocal() as session:
    # Check if admin user exists
    admin = session.query(User).filter(User.email == 'admin@sambanova.com').first()
    
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
        print(f"   Web Login: admin@sambanova.com / admin123")
        print(f"   Voice PIN: {admin.voice_pin}")
        
    else:
        print(f"❌ Admin user NOT found")
        print(f"🔧 Creating admin user...")
        
        admin = User(
            email='admin@sambanova.com',
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
        print(f"   Email: admin@sambanova.com")
        print(f"   Password: admin123")
        print(f"   Voice PIN: 1234")
        print(f"   User ID: {admin.id}")

print(f"\n✅ Done!")

