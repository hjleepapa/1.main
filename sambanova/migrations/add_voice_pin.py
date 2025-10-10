"""
Add voice_pin column to users_sambanova table
Migration for PIN-based voice authentication
"""

import os
from sqlalchemy import create_engine, text

def run_migration():
    """Add voice_pin column to users_sambanova table"""
    
    db_uri = os.getenv("DB_URI")
    if not db_uri:
        print("❌ DB_URI environment variable not set")
        return
    
    print(f"🔧 Connecting to database...")
    engine = create_engine(db_uri)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            check_sql = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users_sambanova' 
                AND column_name = 'voice_pin'
            """)
            
            result = conn.execute(check_sql).fetchone()
            
            if result:
                print(f"✅ voice_pin column already exists, skipping migration")
                return
            
            print(f"🔧 Adding voice_pin column to users_sambanova table...")
            
            # Add voice_pin column
            alter_sql = text("""
                ALTER TABLE users_sambanova 
                ADD COLUMN voice_pin VARCHAR(10) UNIQUE
            """)
            conn.execute(alter_sql)
            
            # Create index for performance
            index_sql = text("""
                CREATE INDEX IF NOT EXISTS idx_users_voice_pin 
                ON users_sambanova(voice_pin)
            """)
            conn.execute(index_sql)
            
            # Set demo admin user's PIN
            update_admin_sql = text("""
                UPDATE users_sambanova 
                SET voice_pin = '1234' 
                WHERE email = 'admin@sambanova.com'
            """)
            conn.execute(update_admin_sql)
            
            conn.commit()
            
            print(f"✅ Migration completed successfully!")
            print(f"✅ voice_pin column added")
            print(f"✅ Index created")
            print(f"✅ Admin user PIN set to '1234'")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()

