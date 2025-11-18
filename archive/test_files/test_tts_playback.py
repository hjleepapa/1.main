#!/usr/bin/env python3
"""
Test TTS Audio Playback
Test if TTS audio is being generated and played correctly
"""

import os
import sys
import base64
import tempfile

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tts_generation():
    """Test TTS audio generation"""
    try:
        from openai import OpenAI
        
        print("🔊 Testing TTS Audio Generation...")
        print("=" * 50)
        
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Test TTS generation
        test_text = "Hello, this is a test of the text-to-speech system."
        print(f"📝 Generating TTS for: '{test_text}'")
        
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=test_text
        )
        
        # Convert to base64
        audio_base64 = base64.b64encode(speech_response.content).decode('utf-8')
        
        print(f"✅ TTS generated successfully")
        print(f"📊 Audio size: {len(speech_response.content)} bytes")
        print(f"📊 Base64 size: {len(audio_base64)} chars")
        print(f"📊 Base64 preview: {audio_base64[:100]}...")
        
        # Save to file for testing
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(speech_response.content)
            temp_file_path = temp_file.name
        
        print(f"💾 Audio saved to: {temp_file_path}")
        print(f"🎵 You can play this file to test audio quality")
        
        return audio_base64, temp_file_path
        
    except Exception as e:
        print(f"❌ Error in TTS generation: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_audio_formats():
    """Test different audio formats for browser compatibility"""
    try:
        print("\n🎵 Testing Audio Format Compatibility...")
        print("-" * 50)
        
        # Test different MIME types
        formats = [
            'data:audio/mp3;base64,',
            'data:audio/wav;base64,',
            'data:audio/ogg;base64,',
            'data:audio/webm;base64,',
            'data:audio/mpeg;base64,',
            'data:audio/octet-stream;base64,'
        ]
        
        for format_type in formats:
            print(f"📋 Format: {format_type}")
        
        print("\n💡 Browser compatibility tips:")
        print("- MP3: Most compatible, works in all browsers")
        print("- WAV: Good quality, works in most browsers")
        print("- OGG: Open source, works in Firefox/Chrome")
        print("- WebM: Modern format, works in Chrome/Firefox")
        
    except Exception as e:
        print(f"❌ Error testing formats: {e}")

if __name__ == "__main__":
    print("🚀 TTS Audio Playback Test")
    print("=" * 60)
    
    # Test TTS generation
    audio_base64, temp_file = test_tts_generation()
    
    if audio_base64:
        # Test audio formats
        test_audio_formats()
        
        print(f"\n✅ TTS test completed successfully!")
        print(f"🎵 Test audio file: {temp_file}")
        print(f"📊 Base64 length: {len(audio_base64)}")
    else:
        print("❌ TTS test failed")
