#!/usr/bin/env python3
"""
Run voice_pin migration standalone
"""

from convonet.migrations.add_voice_pin import run_migration
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    print("🚀 Running voice_pin migration...")
    run_migration()
    print("✅ Done!")

