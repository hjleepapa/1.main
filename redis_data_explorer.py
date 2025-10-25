#!/usr/bin/env python3
"""
Redis Data Explorer for Sambanova Project
Interactive tool to explore and manage Redis data
"""

import json
import time
from datetime import datetime
from sambanova.redis_manager import redis_manager

def print_separator(title=""):
    """Print a visual separator"""
    print("=" * 60)
    if title:
        print(f" {title}")
        print("=" * 60)

def format_timestamp(timestamp):
    """Format timestamp for display"""
    try:
        if isinstance(timestamp, str):
            timestamp = float(timestamp)
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp)

def explore_sessions():
    """Explore session data"""
    print_separator("SESSION DATA")
    
    if not redis_manager.is_available():
        print("❌ Redis is not available")
        return
    
    # Get all session keys
    session_keys = redis_manager.redis_client.keys("session:*")
    print(f"📊 Total sessions: {len(session_keys)}")
    
    if not session_keys:
        print("No sessions found")
        return
    
    # Show recent sessions
    print("\n🔍 Recent Sessions:")
    for key in session_keys[:5]:  # Show first 5
        session_id = key.replace("session:", "")
        session_data = redis_manager.redis_client.hgetall(key)
        
        print(f"\n📱 Session: {session_id}")
        print(f"   User: {session_data.get('user_name', 'Unknown')}")
        print(f"   Authenticated: {session_data.get('authenticated', 'False')}")
        print(f"   Recording: {session_data.get('is_recording', 'False')}")
        
        # Show audio buffer info
        audio_buffer = session_data.get('audio_buffer', '')
        if audio_buffer:
            print(f"   Audio Buffer: {len(audio_buffer)} chars")
            print(f"   Audio Preview: {audio_buffer[:50]}...")
        else:
            print("   Audio Buffer: Empty")
        
        # Show timestamps
        if 'connected_at' in session_data:
            print(f"   Connected: {format_timestamp(session_data['connected_at'])}")
        if 'authenticated_at' in session_data:
            print(f"   Authenticated: {format_timestamp(session_data['authenticated_at'])}")

def explore_user_cache():
    """Explore user cache data"""
    print_separator("USER CACHE DATA")
    
    if not redis_manager.is_available():
        print("❌ Redis is not available")
        return
    
    # Get all user cache keys
    cache_keys = redis_manager.redis_client.keys("user:*")
    print(f"📊 Total user cache entries: {len(cache_keys)}")
    
    if not cache_keys:
        print("No user cache found")
        return
    
    # Group by user
    users = {}
    for key in cache_keys:
        parts = key.split(":")
        if len(parts) >= 3:
            user_id = parts[1]
            data_type = parts[2]
            if user_id not in users:
                users[user_id] = []
            users[user_id].append(data_type)
    
    print(f"\n👥 Users with cached data: {len(users)}")
    for user_id, data_types in users.items():
        print(f"   User {user_id}: {', '.join(data_types)}")

def explore_activity():
    """Explore activity data"""
    print_separator("ACTIVITY DATA")
    
    if not redis_manager.is_available():
        print("❌ Redis is not available")
        return
    
    # Get all activity keys
    activity_keys = redis_manager.redis_client.keys("activity:*")
    print(f"📊 Total activity entries: {len(activity_keys)}")
    
    if not activity_keys:
        print("No activity found")
        return
    
    # Show recent activity
    print("\n📈 Recent Activity:")
    for key in activity_keys[:10]:  # Show first 10
        activity_data = redis_manager.redis_client.get(key)
        if activity_data:
            try:
                activity = json.loads(activity_data)
                print(f"   {activity.get('action', 'Unknown')} - {format_timestamp(activity.get('timestamp', 0))}")
            except:
                print(f"   Invalid activity data: {key}")

def explore_redis_info():
    """Explore Redis server information"""
    print_separator("REDIS SERVER INFO")
    
    if not redis_manager.is_available():
        print("❌ Redis is not available")
        return
    
    try:
        info = redis_manager.redis_client.info()
        
        print(f"🔧 Redis Version: {info.get('redis_version', 'Unknown')}")
        print(f"💾 Used Memory: {info.get('used_memory_human', 'Unknown')}")
        print(f"📊 Total Keys: {info.get('db0', {}).get('keys', 0)}")
        print(f"⏱️  Uptime: {info.get('uptime_in_seconds', 0)} seconds")
        print(f"🔗 Connected Clients: {info.get('connected_clients', 0)}")
        
        # Memory usage percentage
        max_memory = info.get('maxmemory', 0)
        used_memory = info.get('used_memory', 0)
        if max_memory > 0:
            usage_percent = (used_memory / max_memory) * 100
            print(f"📈 Memory Usage: {usage_percent:.1f}%")
        
    except Exception as e:
        print(f"❌ Error getting Redis info: {e}")

def clear_session_data():
    """Clear session data"""
    print_separator("CLEAR SESSION DATA")
    
    if not redis_manager.is_available():
        print("❌ Redis is not available")
        return
    
    # Get all session keys
    session_keys = redis_manager.redis_client.keys("session:*")
    print(f"📊 Found {len(session_keys)} sessions")
    
    if not session_keys:
        print("No sessions to clear")
        return
    
    # Ask for confirmation
    confirm = input("Are you sure you want to clear all session data? (y/N): ")
    if confirm.lower() == 'y':
        deleted_count = 0
        for key in session_keys:
            if redis_manager.redis_client.delete(key):
                deleted_count += 1
        
        print(f"✅ Deleted {deleted_count} sessions")
    else:
        print("❌ Operation cancelled")

def interactive_menu():
    """Interactive menu for Redis exploration"""
    while True:
        print_separator("REDIS DATA EXPLORER")
        print("1. Explore Sessions")
        print("2. Explore User Cache")
        print("3. Explore Activity")
        print("4. Redis Server Info")
        print("5. Clear Session Data")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            explore_sessions()
        elif choice == '2':
            explore_user_cache()
        elif choice == '3':
            explore_activity()
        elif choice == '4':
            explore_redis_info()
        elif choice == '5':
            clear_session_data()
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")
        
        input("\nPress Enter to continue...")

def main():
    """Main function"""
    print("🚀 Redis Data Explorer for Sambanova Project")
    
    # Check Redis connection
    if not redis_manager.is_available():
        print("❌ Redis is not available. Please check your Redis connection.")
        return
    
    print("✅ Redis connection established")
    
    # Run interactive menu
    interactive_menu()

if __name__ == "__main__":
    main()
