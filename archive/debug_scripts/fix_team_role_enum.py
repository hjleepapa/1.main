"""
Fix TeamRole enum case mismatch in database
Convert lowercase role values to uppercase to match Python enum
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

db_uri = os.getenv("DB_URI")
if not db_uri:
    print("❌ DB_URI environment variable not set")
    exit(1)

print(f"🔧 Connecting to database...")
engine = create_engine(db_uri)

try:
    with engine.connect() as conn:
        # First, check current role values
        print(f"\n🔍 Checking current role values...")
        check_sql = text("""
            SELECT DISTINCT role 
            FROM team_memberships_convonet
            ORDER BY role
        """)
        
        result = conn.execute(check_sql)
        current_roles = [row[0] for row in result]
        print(f"Current roles in database: {current_roles}")
        
        # Check the column type
        print(f"\n🔍 Checking column type...")
        type_sql = text("""
            SELECT data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'team_memberships_convonet'
            AND column_name = 'role'
        """)
        
        result = conn.execute(type_sql)
        col_info = result.fetchone()
        if col_info:
            print(f"Column type: {col_info[0]}")
            print(f"UDT name: {col_info[1]}")
        
        # If it's a custom enum type, we need to handle it specially
        if col_info and col_info[1] == 'teamrole':
            print(f"\n⚠️  Column uses PostgreSQL ENUM type 'teamrole'")
            print(f"🔧 This requires special handling...")
            
            # Option 1: Add new uppercase values to the enum
            print(f"\n🔧 Adding uppercase values to enum...")
            try:
                alter_enum_sql = text("""
                    ALTER TYPE teamrole ADD VALUE IF NOT EXISTS 'OWNER';
                    ALTER TYPE teamrole ADD VALUE IF NOT EXISTS 'ADMIN';
                    ALTER TYPE teamrole ADD VALUE IF NOT EXISTS 'MEMBER';
                    ALTER TYPE teamrole ADD VALUE IF NOT EXISTS 'VIEWER';
                """)
                # Note: ALTER TYPE ADD VALUE cannot run in a transaction block
                conn.execute(text("COMMIT"))
                
                # Add values one by one
                for value in ['OWNER', 'ADMIN', 'MEMBER', 'VIEWER']:
                    try:
                        conn.execute(text(f"ALTER TYPE teamrole ADD VALUE IF NOT EXISTS '{value}'"))
                        print(f"  ✅ Added '{value}' to enum")
                    except Exception as e:
                        if 'already exists' in str(e).lower():
                            print(f"  ℹ️  '{value}' already exists")
                        else:
                            print(f"  ⚠️  Could not add '{value}': {e}")
                
            except Exception as e:
                print(f"  ⚠️  Could not modify enum: {e}")
            
            # Option 2: Convert the column to varchar (more flexible)
            print(f"\n🔧 Alternative: Converting column to VARCHAR...")
            try:
                # Drop the enum constraint and convert to varchar
                convert_sql = text("""
                    ALTER TABLE team_memberships_convonet 
                    ALTER COLUMN role TYPE VARCHAR(20) 
                    USING role::text
                """)
                conn.execute(convert_sql)
                conn.commit()
                print(f"  ✅ Column converted to VARCHAR(20)")
                
                # Now update any lowercase values to uppercase
                update_sql = text("""
                    UPDATE team_memberships_convonet
                    SET role = UPPER(role)
                """)
                result = conn.execute(update_sql)
                conn.commit()
                print(f"  ✅ Updated {result.rowcount} rows to uppercase")
                
            except Exception as e:
                print(f"  ❌ Conversion failed: {e}")
                print(f"\n💡 Try manual SQL in PostgreSQL console:")
                print(f"  ALTER TABLE team_memberships_convonet")
                print(f"  ALTER COLUMN role TYPE VARCHAR(20) USING role::text;")
        else:
            # Simple varchar column, just update values
            print(f"\n🔧 Column is VARCHAR, updating values to uppercase...")
            update_sql = text("""
                UPDATE team_memberships_convonet
                SET role = UPPER(role)
                WHERE role IN ('owner', 'admin', 'member', 'viewer')
            """)
            
            result = conn.execute(update_sql)
            conn.commit()
            print(f"✅ Updated {result.rowcount} rows to uppercase")
        
        # Verify the fix
        print(f"\n🔍 Verifying fix...")
        check_sql = text("""
            SELECT DISTINCT role 
            FROM team_memberships_convonet
            ORDER BY role
        """)
        
        result = conn.execute(check_sql)
        new_roles = [row[0] for row in result]
        print(f"Roles after fix: {new_roles}")
        
        print(f"\n✅ Done!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

