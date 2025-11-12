#!/usr/bin/env python3
"""
Test Audio Stream Player
Quick test to verify audio player functionality
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import flask_socketio
        print("✅ Flask-SocketIO imported successfully")
    except ImportError as e:
        print(f"❌ Flask-SocketIO import failed: {e}")
        return False
    
    try:
        import redis
        print("✅ Redis imported successfully")
    except ImportError as e:
        print(f"❌ Redis import failed: {e}")
        return False
    
    try:
        import pyaudio
        print("✅ PyAudio imported successfully")
    except ImportError as e:
        print(f"❌ PyAudio import failed: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    return True

def test_redis_connection():
    """Test Redis connection"""
    print("\n🔍 Testing Redis connection...")
    
    try:
        from convonet.redis_manager import redis_manager
        if redis_manager.is_available():
            print("✅ Redis connection available")
            return True
        else:
            print("❌ Redis connection not available")
            return False
    except ImportError as e:
        print(f"❌ Redis manager import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Redis connection error: {e}")
        return False

def test_audio_system():
    """Test audio system"""
    print("\n🔍 Testing audio system...")
    
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        
        # Get audio device info
        device_count = p.get_device_count()
        print(f"✅ Audio devices found: {device_count}")
        
        # Get default output device
        default_output = p.get_default_output_device_info()
        print(f"✅ Default output device: {default_output['name']}")
        
        p.terminate()
        return True
        
    except Exception as e:
        print(f"❌ Audio system test failed: {e}")
        return False

def test_audio_player_app():
    """Test if audio player app can be imported"""
    print("\n🔍 Testing audio player app...")
    
    try:
        from audio_stream_player import app, socketio
        print("✅ Audio player app imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Audio player app import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Audio player app error: {e}")
        return False

def main():
    """Main test function"""
    print("🎵 Audio Stream Player Test")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test Redis connection
    redis_ok = test_redis_connection()
    
    # Test audio system
    audio_ok = test_audio_system()
    
    # Test audio player app
    app_ok = test_audio_player_app()
    
    print("\n📊 Test Results:")
    print(f"Imports: {'✅' if imports_ok else '❌'}")
    print(f"Redis: {'✅' if redis_ok else '❌'}")
    print(f"Audio: {'✅' if audio_ok else '❌'}")
    print(f"App: {'✅' if app_ok else '❌'}")
    
    if imports_ok and app_ok:
        print("\n🎉 Audio Stream Player is ready!")
        print("Run: python start_audio_player.py")
        print("Then visit: http://localhost:5001")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
    
    return imports_ok and app_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
