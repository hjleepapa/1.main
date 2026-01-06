# How to Reset User Password in users_convonet

## Overview

Passwords in `users_convonet` are stored as **bcrypt hashes** in the `password_hash` column. You cannot directly set a plain text password - it must be hashed first.

---

## Method 1: Python Script (Recommended)

Create a script that uses your existing authentication system:

### Step 1: Create Reset Script

Create file: `reset_user_password.py`

```python
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
```

### Step 2: Run the Script

```bash
# Make script executable
chmod +x reset_user_password.py

# Reset password by email
python reset_user_password.py user@example.com NewPassword123

# Reset password by username
python reset_user_password.py myusername NewPassword123
```

---

## Method 2: Using Python REPL / Flask Shell

### Step 1: Start Python REPL with Database Access

```bash
# From project root
cd "/Users/hj/Web Development Projects/1. Main"
python3
```

### Step 2: Run Commands

```python
import os
import sys
from pathlib import Path

# Add project to path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from convonet.security.auth import JWTAuth
from convonet.models.user_models import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

# Get database URL
db_url = os.getenv('DATABASE_URL') or "postgresql://user:password@localhost:5432/convonet"
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Find user
user_email = "user@example.com"  # Change this
user = db.query(User).filter(User.email == user_email).first()

if user:
    # Hash new password
    jwt_auth = JWTAuth()
    new_password = "NewPassword123"  # Change this
    password_hash = jwt_auth.hash_password(new_password)
    
    # Update user
    user.password_hash = password_hash
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    print(f"✅ Password reset for: {user.email}")
else:
    print(f"❌ User not found: {user_email}")

db.close()
```

---

## Method 3: Direct SQL (Not Recommended - Manual bcrypt Hash)

**⚠️ Warning:** This method requires manually generating a bcrypt hash. Use Method 1 or 2 instead.

### Step 1: Generate bcrypt Hash

```python
import bcrypt

password = "NewPassword123"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
print(hashed.decode('utf-8'))
```

### Step 2: Update Database

```sql
-- Connect to database
psql -U postgres -d convonet

-- Update password (replace with generated hash)
UPDATE users_convonet 
SET password_hash = '$2b$12$...your_bcrypt_hash_here...',
    updated_at = NOW()
WHERE email = 'user@example.com';

-- Verify update
SELECT email, username, LEFT(password_hash, 20) as hash_preview 
FROM users_convonet 
WHERE email = 'user@example.com';
```

---

## Method 4: Using Flask CLI (If Available)

If your Flask app has CLI commands set up:

```bash
# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/convonet"

# Run Flask shell
flask shell

# Then in Flask shell:
from convonet.security.auth import JWTAuth
from convonet.models.user_models import User
from app import db

user = User.query.filter_by(email='user@example.com').first()
jwt_auth = JWTAuth()
user.password_hash = jwt_auth.hash_password('NewPassword123')
db.session.commit()
```

---

## Quick Reference: Find User First

Before resetting, you may want to find the user:

### By Email:
```python
user = db.query(User).filter(User.email == 'user@example.com').first()
```

### By Username:
```python
user = db.query(User).filter(User.username == 'myusername').first()
```

### List All Users:
```python
users = db.query(User).all()
for user in users:
    print(f"{user.email} ({user.username}) - {user.full_name}")
```

---

## Security Best Practices

1. **Use Strong Passwords**: Minimum 8 characters, mix of letters, numbers, symbols
2. **Never Store Plain Text**: Always hash passwords before storing
3. **Use Existing Auth System**: Use `JWTAuth.hash_password()` method
4. **Update Timestamp**: Always update `updated_at` field
5. **Verify User Exists**: Check user exists before updating
6. **Log Password Resets**: Consider logging password reset actions for audit

---

## Troubleshooting

### Error: "User not found"
- Check email/username spelling
- Verify user exists in database:
  ```sql
  SELECT email, username FROM users_convonet;
  ```

### Error: "Database connection failed"
- Check `DATABASE_URL` environment variable
- Verify database credentials
- Ensure database is running

### Error: "Module not found"
- Ensure you're running from project root
- Check Python path includes project directory
- Install dependencies: `pip install -r requirements.txt`

---

## Example: Complete Reset Workflow

```bash
# 1. Navigate to project
cd "/Users/hj/Web Development Projects/1. Main"

# 2. Set environment variables (if needed)
export DATABASE_URL="postgresql://user:password@localhost:5432/convonet"

# 3. Run reset script
python reset_user_password.py user@example.com SecurePassword123!

# Output:
# ✅ Password reset successful for user: user@example.com (myusername)
#    User ID: 123e4567-e89b-12d3-a456-426614174000
#    Full Name: John Doe
```

---

## Additional: Reset Voice PIN

If you also need to reset the voice PIN (for Twilio authentication):

```python
# In Python REPL or script
user = db.query(User).filter(User.email == 'user@example.com').first()
user.voice_pin = '1234'  # 4-6 digit PIN
db.commit()
```

Or via SQL:
```sql
UPDATE users_convonet 
SET voice_pin = '1234'
WHERE email = 'user@example.com';
```

---

## Recommended Approach

**Use Method 1 (Python Script)** - It's:
- ✅ Safe (uses existing auth system)
- ✅ Reusable
- ✅ Includes error handling
- ✅ Easy to use
- ✅ Follows best practices

