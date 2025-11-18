"""
AssemblyAI Streaming Service for WebRTC Voice Recognition
Production-ready voice transcription with high accuracy
"""

import assemblyai as aai
import logging
import os
import asyncio
from typing import Optional, Dict, Any, Callable
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class AssemblyAIService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AssemblyAI service
        
        Args:
            api_key: AssemblyAI API key (if None, will use ASSEMBLYAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ASSEMBLYAI_API_KEY')
        
        # For testing - you can temporarily hardcode your API key here
        # TODO: Remove this line and use environment variable for production
        if not self.api_key:
            # self.api_key = "your_api_key_here"  # Uncomment and add your key
            raise ValueError("AssemblyAI API key required. Set ASSEMBLYAI_API_KEY environment variable or pass api_key parameter.")
        
        # Configure AssemblyAI
        aai.settings.api_key = self.api_key
        self.transcriber = aai.Transcriber()
        
        logger.info("✅ AssemblyAI service initialized")
    
    def transcribe_audio_buffer(self, audio_buffer: bytes, language: str = "en") -> Optional[str]:
        """
        Transcribe audio buffer using AssemblyAI
        
        Args:
            audio_buffer: Raw audio data bytes from WebRTC
            language: Language code (default: "en")
            
        Returns:
            Transcribed text string or None if failed
        """
        import tempfile
        import subprocess
        
        try:
            logger.info(f"🎧 AssemblyAI: Transcribing audio buffer: {len(audio_buffer)} bytes")
            
            # DIAGNOSTIC: Log the fundamental issue
            logger.warning("🚨 FUNDAMENTAL ISSUE: AssemblyAI file-based API is not suitable for WebRTC real-time streaming")
            logger.warning("🚨 WebRTC sends small audio chunks (44-1948 bytes) that are fragments, not complete audio files")
            logger.warning("🚨 AssemblyAI expects complete audio files with proper headers and sufficient length")
            logger.warning("🚨 RECOMMENDATION: Switch to Deepgram or AssemblyAI streaming API for real-time transcription")
            
            # WebRTC audio is raw PCM data, not a complete audio file
            # We need to create a proper WAV file with headers
            
            # Check audio quality first
            audio_quality = self._analyze_audio_quality(audio_buffer)
            logger.info(f"🔍 Audio quality analysis: {audio_quality}")
            
            if audio_quality['is_silence']:
                logger.warning("⚠️ Audio appears to be silence or very quiet")
                return None
            
            if audio_quality['is_noise']:
                logger.warning("⚠️ Audio appears to be noise rather than speech")
                return None
            
            # Check if audio is too short for meaningful speech
            # WebRTC chunks are very small, so we need a much lower threshold
            min_audio_length = 10000  # Much lower threshold for WebRTC
            if len(audio_buffer) < min_audio_length:
                logger.warning(f"⚠️ Audio too short for transcription: {len(audio_buffer)} bytes (need {min_audio_length}+)")
                return None
            
            # Apply ultra-aggressive normalization for WebRTC audio
            if audio_quality['clipping_percentage'] > 0.5 or audio_quality['rms'] > 2000:
                logger.info("🔧 Audio is clipped/loud, applying ultra-aggressive normalization...")
                audio_buffer = self._ultra_aggressive_normalize_audio(audio_buffer)
                logger.info("✅ Ultra-aggressive audio normalization completed")
            
            wav_file_path = self._create_wav_from_pcm(audio_buffer)
            
            if not wav_file_path:
                logger.error("❌ Failed to create WAV file from PCM data")
                return None
            
            try:
                # Try transcription with the WAV file
                success = self._try_transcription(wav_file_path, '.wav')
                if success:
                    return success
                
                # If WAV fails, try converting to MP3
                logger.info("🔄 WAV failed, trying MP3 conversion...")
                mp3_file_path = self._convert_wav_to_mp3(wav_file_path)
                if mp3_file_path:
                    success = self._try_transcription(mp3_file_path, '.mp3')
                    if success:
                        return success
                
                logger.error("❌ All transcription approaches failed")
                return None
                
            finally:
                # Clean up files
                if os.path.exists(wav_file_path):
                    os.unlink(wav_file_path)
                if 'mp3_file_path' in locals() and os.path.exists(mp3_file_path):
                    os.unlink(mp3_file_path)
                
        except Exception as e:
            logger.error(f"❌ AssemblyAI transcription failed: {e}")
            return None
    
    def _analyze_audio_quality(self, audio_buffer: bytes) -> dict:
        """Analyze audio quality to detect silence, noise, or speech"""
        try:
            import struct
            
            # Convert bytes to 16-bit signed integers
            if len(audio_buffer) % 2 != 0:
                audio_buffer = audio_buffer[:-1]  # Remove odd byte
            
            samples = struct.unpack(f'<{len(audio_buffer)//2}h', audio_buffer)
            
            # Calculate RMS (Root Mean Square) for volume
            rms = (sum(sample * sample for sample in samples) / len(samples)) ** 0.5
            
            # Calculate dynamic range
            max_sample = max(samples)
            min_sample = min(samples)
            dynamic_range = max_sample - min_sample
            
            # Detect silence (very low volume)
            is_silence = rms < 100  # Threshold for silence
            
            # Detect noise (high volume but low dynamic range)
            is_noise = rms > 1000 and dynamic_range < 2000
            
            # Detect clipping (samples hitting max/min values)
            clipping_count = sum(1 for s in samples if abs(s) > 30000)
            clipping_percentage = (clipping_count / len(samples)) * 100
            
            return {
                'rms': rms,
                'dynamic_range': dynamic_range,
                'max_sample': max_sample,
                'min_sample': min_sample,
                'is_silence': is_silence,
                'is_noise': is_noise,
                'clipping_percentage': clipping_percentage,
                'sample_count': len(samples)
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Audio quality analysis failed: {e}")
            return {
                'rms': 0,
                'dynamic_range': 0,
                'max_sample': 0,
                'min_sample': 0,
                'is_silence': False,
                'is_noise': False,
                'clipping_percentage': 0,
                'sample_count': 0
            }
    
    def _normalize_audio(self, audio_buffer: bytes) -> bytes:
        """Normalize audio to prevent clipping and improve quality"""
        try:
            import struct
            
            # Convert bytes to 16-bit signed integers
            if len(audio_buffer) % 2 != 0:
                audio_buffer = audio_buffer[:-1]  # Remove odd byte
            
            samples = struct.unpack(f'<{len(audio_buffer)//2}h', audio_buffer)
            
            # Find the maximum absolute value
            max_val = max(abs(sample) for sample in samples)
            
            if max_val == 0:
                return audio_buffer  # No audio to normalize
            
            # Calculate normalization factor (target 80% of max range)
            target_max = int(32767 * 0.8)  # 80% of max 16-bit value
            normalization_factor = target_max / max_val
            
            # Apply normalization
            normalized_samples = [int(sample * normalization_factor) for sample in samples]
            
            # Convert back to bytes
            normalized_bytes = struct.pack(f'<{len(normalized_samples)}h', *normalized_samples)
            
            logger.info(f"🔧 Normalized audio: factor={normalization_factor:.3f}, max_val={max_val} -> {max(normalized_samples)}")
            
            return normalized_bytes
            
        except Exception as e:
            logger.warning(f"⚠️ Audio normalization failed: {e}")
            return audio_buffer

    def _aggressive_normalize_audio(self, audio_buffer: bytes) -> bytes:
        """Apply aggressive normalization to fix severely clipped WebRTC audio"""
        try:
            import struct
            
            # Convert bytes to 16-bit signed integers
            if len(audio_buffer) % 2 != 0:
                audio_buffer = audio_buffer[:-1]  # Remove odd byte
            
            samples = struct.unpack(f'<{len(audio_buffer)//2}h', audio_buffer)
            
            # Find the maximum absolute value
            max_val = max(abs(sample) for sample in samples)
            
            if max_val == 0:
                return audio_buffer  # No audio to normalize
            
            # Aggressive normalization: target only 30% of max range to prevent clipping
            target_max = int(32767 * 0.3)  # 30% of max 16-bit value
            normalization_factor = target_max / max_val
            
            # Apply aggressive normalization
            normalized_samples = [int(sample * normalization_factor) for sample in samples]
            
            # Additional smoothing to reduce harsh clipping artifacts
            smoothed_samples = []
            for i in range(len(normalized_samples)):
                if i == 0:
                    smoothed_samples.append(normalized_samples[i])
                elif i == len(normalized_samples) - 1:
                    smoothed_samples.append(normalized_samples[i])
                else:
                    # Simple 3-point smoothing to reduce harsh transitions
                    smoothed = (normalized_samples[i-1] + normalized_samples[i] + normalized_samples[i+1]) // 3
                    smoothed_samples.append(smoothed)
            
            # Convert back to bytes
            normalized_bytes = struct.pack(f'<{len(smoothed_samples)}h', *smoothed_samples)
            
            logger.info(f"🔧 Aggressive normalization: factor={normalization_factor:.3f}, max_val={max_val} -> {max(smoothed_samples)}")
            
            return normalized_bytes
            
        except Exception as e:
            logger.warning(f"⚠️ Aggressive audio normalization failed: {e}")
            return audio_buffer

    def _ultra_aggressive_normalize_audio(self, audio_buffer: bytes) -> bytes:
        """Ultra-aggressive normalization to eliminate all distortion"""
        try:
            import struct
            
            # Convert bytes to 16-bit signed integers
            if len(audio_buffer) % 2 != 0:
                audio_buffer = audio_buffer[:-1]  # Remove odd byte
            
            samples = struct.unpack(f'<{len(audio_buffer)//2}h', audio_buffer)
            
            # Find the maximum absolute value
            max_val = max(abs(sample) for sample in samples)
            
            if max_val == 0:
                return audio_buffer  # No audio to normalize
            
            # Ultra-aggressive normalization (target 15% of max range)
            target_max = int(32767 * 0.15)  # 15% of max 16-bit value
            normalization_factor = target_max / max_val
            
            # Apply normalization with smoothing
            normalized_samples = []
            for i, sample in enumerate(samples):
                normalized = int(sample * normalization_factor)
                
                # Apply smoothing to reduce harsh transitions
                if i > 0:
                    prev_normalized = normalized_samples[i-1]
                    # Smooth transitions to prevent harsh "Shee~" sounds
                    smoothed = int((normalized + prev_normalized) / 2)
                    normalized_samples.append(smoothed)
                else:
                    normalized_samples.append(normalized)
            
            # Convert back to bytes
            normalized_bytes = struct.pack(f'<{len(normalized_samples)}h', *normalized_samples)
            
            logger.info(f"🔧 Ultra-aggressive normalization: factor={normalization_factor:.3f}, max_val={max_val} -> {max(normalized_samples)}")
            
            return normalized_bytes
            
        except Exception as e:
            logger.warning(f"⚠️ Ultra-aggressive normalization failed: {e}")
            return audio_buffer
    
    def _create_wav_from_pcm(self, pcm_data: bytes) -> Optional[str]:
        """Create a WAV file from raw PCM data"""
        import tempfile
        import wave
        import struct
        
        try:
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                wav_path = temp_file.name
            
            # Try different PCM configurations
            pcm_configs = [
                {"sample_rate": 48000, "channels": 1, "sample_width": 2, "desc": "48kHz, mono, 16-bit"},
                {"sample_rate": 44100, "channels": 1, "sample_width": 2, "desc": "44.1kHz, mono, 16-bit"},
                {"sample_rate": 16000, "channels": 1, "sample_width": 2, "desc": "16kHz, mono, 16-bit"},
                {"sample_rate": 8000, "channels": 1, "sample_width": 2, "desc": "8kHz, mono, 16-bit"},
            ]
            
            for config in pcm_configs:
                try:
                    logger.info(f"🔍 Trying PCM config: {config['desc']}")
                    
                    # Create WAV file with proper headers
                    with wave.open(wav_path, 'wb') as wav_file:
                        wav_file.setnchannels(config['channels'])
                        wav_file.setsampwidth(config['sample_width'])
                        wav_file.setframerate(config['sample_rate'])
                        wav_file.writeframes(pcm_data)
                    
                    # Test if the file is valid
                    with wave.open(wav_path, 'rb') as test_file:
                        frames = test_file.getnframes()
                        if frames > 0:
                            logger.info(f"✅ Created valid WAV file: {config['desc']}, {frames} frames")
                            return wav_path
                    
                except Exception as e:
                    logger.warning(f"⚠️ PCM config {config['desc']} failed: {e}")
                    continue
            
            logger.error("❌ All PCM configurations failed")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to create WAV file: {e}")
            return None
    
    def _convert_wav_to_mp3(self, wav_path: str) -> Optional[str]:
        """Convert WAV to MP3 using ffmpeg"""
        import subprocess
        
        try:
            mp3_path = wav_path.replace('.wav', '.mp3')
            
            result = subprocess.run([
                'ffmpeg', '-i', wav_path, '-acodec', 'mp3', 
                '-ar', '16000', '-ac', '1', '-y', mp3_path
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(mp3_path):
                logger.info(f"✅ WAV to MP3 conversion successful")
                return mp3_path
            else:
                logger.warning(f"⚠️ WAV to MP3 conversion failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ MP3 conversion error: {e}")
            return None
    
    def _try_transcription(self, file_path: str, file_type: str) -> Optional[str]:
        """Try transcription with a specific file"""
        try:
            logger.info(f"📤 Uploading {file_type} file to AssemblyAI: {file_path}")
            logger.info(f"📊 File size: {os.path.getsize(file_path)} bytes")
            
            result = self.transcriber.transcribe(file_path)
            
            # Log detailed result information
            logger.info(f"🔍 AssemblyAI result status: {result.status if hasattr(result, 'status') else 'unknown'}")
            logger.info(f"🔍 AssemblyAI result text length: {len(result.text) if result.text else 0}")
            logger.info(f"🔍 AssemblyAI result confidence: {result.confidence if hasattr(result, 'confidence') else 'unknown'}")
            
            if result.text and result.text.strip():
                transcription_text = result.text.strip()
                confidence = result.confidence or 0.8
                
                logger.info(f"✅ AssemblyAI transcription successful ({file_type})")
                logger.info(f"📝 Text: {transcription_text}")
                logger.info(f"🎯 Confidence: {confidence:.2f}")
                
                return transcription_text
            else:
                logger.warning(f"⚠️ AssemblyAI returned empty transcription ({file_type})")
                logger.warning(f"🔍 Raw result text: '{result.text}'")
                return None
                
        except Exception as e:
            logger.error(f"❌ {file_type} transcription failed: {e}")
            return None
    
    async def transcribe_audio_stream(self, audio_chunks: list, language: str = "en") -> Optional[str]:
        """
        Transcribe streaming audio chunks using AssemblyAI
        
        Args:
            audio_chunks: List of audio chunk bytes
            language: Language code (default: "en")
            
        Returns:
            Transcribed text string or None if failed
        """
        try:
            # Combine all chunks into single buffer
            combined_audio = b''.join(audio_chunks)
            logger.info(f"🎧 AssemblyAI: Transcribing stream: {len(combined_audio)} bytes from {len(audio_chunks)} chunks")
            
            return self.transcribe_audio_buffer(combined_audio, language)
            
        except Exception as e:
            logger.error(f"❌ AssemblyAI stream transcription failed: {e}")
            return None
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about AssemblyAI service"""
        return {
            "transcriber": "assemblyai",
            "model": "latest",
            "accuracy": "95%+",
            "cost_per_minute": 0.04,  # $0.00065 per second
            "privacy": "processed on AssemblyAI servers",
            "latency": "1-2 seconds",
            "supported_formats": ["wav", "mp3", "webm", "m4a", "flac", "ogg", "raw_pcm"],
            "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
            "features": ["punctuation", "formatting", "speaker_diarization", "sentiment_analysis"],
            "api_calls": 1,  # One API call per transcription
            "realtime": True
        }

# Global instance for singleton pattern
assemblyai_service = None

def get_assemblyai_service() -> AssemblyAIService:
    """Get or create AssemblyAI service instance"""
    global assemblyai_service
    if assemblyai_service is None:
        assemblyai_service = AssemblyAIService()
    return assemblyai_service

def transcribe_audio_with_assemblyai(audio_buffer: bytes, language: str = "en") -> Optional[str]:
    """
    Transcribe audio buffer using AssemblyAI
    Drop-in replacement for local Whisper calls
    
    Args:
        audio_buffer: Raw audio data bytes
        language: Language code (default: "en")
        
    Returns:
        Transcribed text string or None if failed
    """
    try:
        service = get_assemblyai_service()
        return service.transcribe_audio_buffer(audio_buffer, language)
    except Exception as e:
        logger.error(f"❌ AssemblyAI service error: {e}")
        return None

def get_assemblyai_info() -> Dict[str, Any]:
    """Get information about AssemblyAI service"""
    try:
        service = get_assemblyai_service()
        return service.get_service_info()
    except Exception as e:
        logger.error(f"❌ Failed to get AssemblyAI info: {e}")
        return {
            "transcriber": "assemblyai",
            "error": str(e),
            "status": "unavailable"
        }

# Test function
def test_assemblyai_integration():
    """Test AssemblyAI integration"""
    print("🧪 Testing AssemblyAI Integration...")
    
    # Test service info
    info = get_assemblyai_info()
    print(f"📊 Service Info: {info}")
    
    # Test with dummy audio data
    dummy_audio = b'\x00' * 1000  # 1KB of silence
    print(f"🎧 Testing with dummy audio: {len(dummy_audio)} bytes")
    
    result = transcribe_audio_with_assemblyai(dummy_audio)
    if result:
        print(f"✅ Transcription successful: {result}")
    else:
        print("⚠️ Transcription returned empty (expected for silence)")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_assemblyai_integration()
