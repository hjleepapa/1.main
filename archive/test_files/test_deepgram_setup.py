#!/usr/bin/env python3
"""
Test script for Deepgram WebRTC integration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deepgram_setup():
    """Test Deepgram API key and service setup"""
    print("🧪 Testing Deepgram Setup...")
    
    # Check API key
    api_key = os.getenv('DEEPGRAM_API_KEY')
    if not api_key:
        print("❌ DEEPGRAM_API_KEY not found in environment variables")
        print("💡 Please add DEEPGRAM_API_KEY=your_api_key_here to your .env file")
        return False
    
    print(f"✅ DEEPGRAM_API_KEY found: {api_key[:8]}...")
    
    # Test Deepgram service import
    try:
        from deepgram_service import get_deepgram_service
        print("✅ Deepgram service import successful")
    except ImportError as e:
        print(f"❌ Failed to import Deepgram service: {e}")
        return False
    
    # Test Deepgram service initialization
    try:
        service = get_deepgram_service()
        print("✅ Deepgram service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Deepgram service: {e}")
        return False
    
    # Test WebRTC integration
    try:
        from deepgram_webrtc_integration import get_deepgram_webrtc_info
        info = get_deepgram_webrtc_info()
        print("✅ Deepgram WebRTC integration successful")
        print(f"📊 Model: {info['model']}")
        print(f"📊 Latency: {info['latency']}")
        print(f"📊 Cost: ${info['cost_per_minute']}/minute")
    except Exception as e:
        print(f"❌ Failed to test WebRTC integration: {e}")
        return False
    
    print("\n🎉 Deepgram setup is complete and ready for testing!")
    return True

if __name__ == "__main__":
    success = test_deepgram_setup()
    sys.exit(0 if success else 1)
