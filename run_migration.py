#!/usr/bin/env python3
"""
Run database migration for team collaboration features
This script should be run during deployment to ensure tables are created
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_team_migration():
    """Run the team collaboration migration"""
    try:
        print("🔄 Running team collaboration migration...")
        
        # Import and run the migration
        from convonet.migrations.add_team_collaboration import run_migration
        
        success = run_migration()
        
        if success:
            print("✅ Team collaboration migration completed successfully!")
            return True
        else:
            print("❌ Team collaboration migration failed!")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_team_migration()
    if not success:
        sys.exit(1)
