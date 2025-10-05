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
    
    # Run the team collaboration migration
    try:
        print("🔄 Running team collaboration migration...")
        result = subprocess.run([sys.executable, "run_migration.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Migration completed successfully")
            print("Migration output:", result.stdout)
        else:
            print("❌ Migration failed")
            print("Migration error:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Migration timed out")
        return False
    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        return False
    
    print("🎉 Deployment setup completed successfully!")
    return True

if __name__ == "__main__":
    success = setup_deployment()
    if not success:
        sys.exit(1)
