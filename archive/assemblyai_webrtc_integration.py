"""
AssemblyAI Integration for WebRTC Voice Server
Replaces local Whisper with production-ready AssemblyAI
"""

import logging
import os
from typing import Optional, Dict, Any
from assemblyai_service import transcribe_audio_with_assemblyai, get_assemblyai_info

logger = logging.getLogger(__name__)

def transcribe_audio_with_assemblyai_webrtc(audio_buffer: bytes, language: str = "en") -> Optional[str]:
    """
    Transcribe WebRTC audio buffer using AssemblyAI
    Drop-in replacement for local Whisper calls
    
    Args:
        audio_buffer: Raw audio data bytes from WebRTC
        language: Language code (default: "en")
        
    Returns:
        Transcribed text string or None if failed
    """
    try:
        logger.info(f"🎧 AssemblyAI WebRTC: Processing audio buffer: {len(audio_buffer)} bytes")
        
        # Check if AssemblyAI API key is available
        api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not api_key:
            logger.error("❌ AssemblyAI API key not found. Please set ASSEMBLYAI_API_KEY environment variable.")
            return None
        
        # AssemblyAI can handle raw WebRTC audio data directly
        # No need for complex format conversion or reconstruction
        result = transcribe_audio_with_assemblyai(audio_buffer, language)
        
        if result:
            logger.info(f"✅ AssemblyAI WebRTC transcription successful: {result}")
            return result
        else:
            logger.warning("⚠️ AssemblyAI WebRTC transcription returned empty result")
            return None
            
    except Exception as e:
        logger.error(f"❌ AssemblyAI WebRTC transcription error: {e}")
        return None

def get_assemblyai_webrtc_info() -> Dict[str, Any]:
    """Get information about AssemblyAI WebRTC service"""
    try:
        info = get_assemblyai_info()
        info.update({
            "webrtc_ready": True,
            "no_format_conversion_needed": True,
            "handles_raw_audio": True,
            "production_ready": True
        })
        return info
    except Exception as e:
        logger.error(f"❌ Failed to get AssemblyAI WebRTC info: {e}")
        return {
            "transcriber": "assemblyai_webrtc",
            "error": str(e),
            "status": "unavailable"
        }

# Test function for WebRTC integration
def test_assemblyai_webrtc_integration():
    """Test AssemblyAI WebRTC integration"""
    print("🧪 Testing AssemblyAI WebRTC Integration...")
    
    # Test service info
    info = get_assemblyai_webrtc_info()
    print(f"📊 WebRTC Service Info: {info}")
    
    # Test with WebRTC-like audio data
    webrtc_audio = b'\x1a\x45\xdf\xa3' + b'\x00' * 1000  # WebM header + audio data
    print(f"🎧 Testing with WebRTC-like audio: {len(webrtc_audio)} bytes")
    
    result = transcribe_audio_with_assemblyai_webrtc(webrtc_audio)
    if result:
        print(f"✅ WebRTC transcription successful: {result}")
    else:
        print("⚠️ WebRTC transcription returned empty (expected for test data)")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_assemblyai_webrtc_integration()
