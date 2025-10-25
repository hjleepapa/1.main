#!/usr/bin/env python3
"""
Start Audio Stream Player
Launches the audio stream player application
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask',
        'flask_socketio', 
        'redis',
        'pyaudio',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is not installed")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements_audio_player.txt")
        return False
    
    return True

def check_redis_connection():
    """Check Redis connection"""
    try:
        from sambanova.redis_manager import redis_manager
        if redis_manager.is_available():
            print("✅ Redis connection available")
            return True
        else:
            print("❌ Redis connection not available")
            return False
    except ImportError:
        print("❌ Redis manager not available")
        return False

def start_audio_player():
    """Start the audio stream player"""
    print("🎵 Starting Audio Stream Player...")
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Missing dependencies. Please install required packages.")
        return False
    
    # Check Redis connection
    redis_available = check_redis_connection()
    if not redis_available:
        print("⚠️ Redis not available - some features will be limited")
    
    # Start the application
    try:
        print("🚀 Launching audio stream player on http://localhost:5001")
        print("Press Ctrl+C to stop")
        
        # Import and run the audio player
        from audio_stream_player import app, socketio
        socketio.run(app, debug=True, host='0.0.0.0', port=5001)
        
    except KeyboardInterrupt:
        print("\n👋 Audio stream player stopped")
    except Exception as e:
        print(f"❌ Error starting audio player: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("=" * 60)
    print("🎵 Audio Stream Player for Sambanova Project")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('audio_stream_player.py'):
        print("❌ audio_stream_player.py not found. Please run from the project root.")
        return
    
    # Start the audio player
    start_audio_player()

if __name__ == "__main__":
    main()
