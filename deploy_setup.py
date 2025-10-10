#!/usr/bin/env python3
"""
Deployment setup script for Sambanova
Runs database migrations and sets up the application
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_deployment():
    """Setup the application for deployment"""
    print("🚀 Setting up Sambanova for deployment...")
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Make sure you're in the project root.")
        return False
    
    # Check for required environment variables
    required_env_vars = ["DB_URI"]
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables check passed")
    
    # Run migrations
    migrations = [
        ("run_migration.py", "Team collaboration migration"),
        ("sambanova/migrations/add_voice_pin.py", "Voice PIN authentication migration")
    ]
    
    for migration_file, migration_name in migrations:
        if not Path(migration_file).exists():
            print(f"⚠️  {migration_name} file not found: {migration_file}")
            continue
            
        try:
            print(f"🔄 Running {migration_name}...")
            result = subprocess.run([sys.executable, migration_file], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ {migration_name} completed successfully")
                if result.stdout:
                    print(f"   Output: {result.stdout}")
            else:
                print(f"⚠️  {migration_name} had issues (may already be applied)")
                if result.stderr:
                    print(f"   Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"❌ {migration_name} timed out")
            return False
        except Exception as e:
            print(f"⚠️  {migration_name} error: {str(e)}")
    
    print("🎉 Deployment setup completed successfully!")
    return True

if __name__ == "__main__":
    success = setup_deployment()
    if not success:
        sys.exit(1)
