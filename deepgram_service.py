from deepgram import DeepgramClient
import logging
import os
import asyncio
from typing import Optional, Dict, Any, Callable
import base64
from dotenv import load_dotenv
import tempfile
import wave
import struct
import requests
import numpy as np

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class DeepgramService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Deepgram service for real-time WebRTC streaming
        
        Args:
            api_key: Deepgram API key (if None, will use DEEPGRAM_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('DEEPGRAM_API_KEY')
        
        if not self.api_key:
            raise ValueError("Deepgram API key required. Set DEEPGRAM_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize Deepgram client
        self.client = DeepgramClient(api_key=self.api_key)
        
        logger.info("✅ Deepgram service initialized for real-time streaming")
    
    def transcribe_audio_buffer(self, audio_buffer: bytes, language: str = "en") -> Optional[str]:
        """
        Transcribe audio buffer using Deepgram's streaming API
        
        Args:
            audio_buffer: Raw audio data bytes from WebRTC
            language: Language code (default: "en")
            
        Returns:
            Transcribed text string or None if failed
        """
        try:
                   logger.info(f"🎧 Deepgram: Transcribing audio buffer: {len(audio_buffer)} bytes")
                   
                   # Check if audio is too short for meaningful speech
                   min_audio_length = 1000  # Much lower threshold for Deepgram streaming
                   if len(audio_buffer) < min_audio_length:
                       logger.warning(f"⚠️ Audio too short for transcription: {len(audio_buffer)} bytes (need {min_audio_length}+)")
                       return None
                   
                   # Detect WebM/EBML header (Opus in WebM from MediaRecorder)
                   is_webm = len(audio_buffer) >= 4 and audio_buffer[:4] == b"\x1a\x45\xdf\xa3"
                   if is_webm:
                       logger.info("🧭 Detected WebM/EBML header - sending as audio/webm to Deepgram")
                       with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
                           webm_path = temp_file.name
                           temp_file.write(audio_buffer)
                       try:
                           result = self._transcribe_file(webm_path, language)
                           return result
                       finally:
                           if os.path.exists(webm_path):
                               os.unlink(webm_path)
                   
                   # Analyze audio quality before PCM processing
                   audio_quality = self._analyze_audio_quality(audio_buffer)
                   logger.info(f"🔍 Audio quality analysis: {audio_quality}")
                   
                   if audio_quality.get('is_silence', False):
                       logger.warning("⚠️ Audio appears to be silence, skipping transcription")
                       return None
                   
                   if audio_quality.get('clipping_percentage', 0) > 10:
                       logger.warning(f"⚠️ Audio has severe clipping ({audio_quality.get('clipping_percentage', 0):.1f}%), may affect transcription quality")
                   
                   # Fallback: treat as raw PCM and create WAV
                   wav_file_path = self._create_wav_from_pcm(audio_buffer)
                   if not wav_file_path:
                       logger.error("❌ Failed to create WAV file from PCM data")
                       return None
                   try:
                       result = self._transcribe_file(wav_file_path, language)
                       return result
                   finally:
                       if os.path.exists(wav_file_path):
                           os.unlink(wav_file_path)
        except Exception as e:
            logger.error(f"❌ Deepgram transcription failed: {e}")
            return None
    
    def _create_wav_from_pcm(self, pcm_data: bytes) -> Optional[str]:
        """Create a WAV file from raw PCM data optimized for Deepgram"""
        try:
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                wav_path = temp_file.name
            
            # Try different PCM configurations optimized for Deepgram
            # Start with WebRTC standard format first, then Deepgram's preferred format
            pcm_configs = [
                {"sample_rate": 48000, "channels": 1, "sample_width": 2, "desc": "48kHz, mono, 16-bit (WebRTC standard)"},
                {"sample_rate": 16000, "channels": 1, "sample_width": 2, "desc": "16kHz, mono, 16-bit (Deepgram optimized)"},
                {"sample_rate": 44100, "channels": 1, "sample_width": 2, "desc": "44.1kHz, mono, 16-bit (CD quality)"},
                {"sample_rate": 8000, "channels": 1, "sample_width": 2, "desc": "8kHz, mono, 16-bit (telephone quality)"},
            ]
            
            for config in pcm_configs:
                try:
                    logger.info(f"🔍 Trying PCM config: {config['desc']}")
                    
                    # Write WAV file with proper headers
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
    
    def _transcribe_file(self, file_path: str, language: str) -> Optional[str]:
        """Transcribe a file using Deepgram's HTTP API"""
        try:
            logger.info(f"📤 Uploading file to Deepgram: {file_path}")
            logger.info(f"📊 File size: {os.path.getsize(file_path)} bytes")
            
            # Use Deepgram's HTTP API directly
            url = "https://api.deepgram.com/v1/listen"
            
            # Configure parameters for prerecorded/batch API (no streaming-only params)
            params = {
                "model": "nova-2",  # Use Deepgram's latest model
                "language": language,
                "smart_format": "true",  # Enable smart formatting
                "punctuate": "true",     # Add punctuation
                "alternatives": "1",     # Single alternative
                "detect_language": "false",  # Use specified language
            }
            
            # Read the file
            with open(file_path, 'rb') as audio_file:
                buffer_data = audio_file.read()
            
            # Choose content type by extension
            content_type = "audio/wav"
            if file_path.lower().endswith('.webm'):
                content_type = "audio/webm"
            
            # Make the request
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": content_type
            }
            
            response = requests.post(url, params=params, headers=headers, data=buffer_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"📋 Deepgram API Response: {result}")
                
                # Extract transcription text
                if result.get("results") and result["results"].get("channels"):
                    channel = result["results"]["channels"][0]
                    logger.info(f"📊 Channel data: {channel}")
                    
                    if channel.get("alternatives"):
                        alternative = channel["alternatives"][0]
                        transcription_text = alternative.get("transcript")
                        confidence = alternative.get("confidence", 0)
                        
                        logger.info(f"📝 Raw transcript: '{transcription_text}'")
                        logger.info(f"🎯 Confidence: {confidence:.2f}")
                        
                        if transcription_text and transcription_text.strip():
                            logger.info(f"✅ Deepgram transcription successful")
                            logger.info(f"📝 Text: {transcription_text}")
                            
                            return transcription_text.strip()
                        else:
                            logger.warning("⚠️ Deepgram returned empty transcription")
                            logger.warning(f"🔍 Alternative data: {alternative}")
                            return None
                    else:
                        logger.warning("⚠️ Deepgram returned no alternatives")
                        logger.warning(f"🔍 Channel data: {channel}")
                        return None
                else:
                    logger.warning("⚠️ Deepgram returned no results")
                    logger.warning(f"🔍 Full response: {result}")
                    return None
            else:
                logger.error(f"❌ Deepgram API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Deepgram file transcription failed: {e}")
            return None
    
    def _analyze_audio_quality(self, audio_buffer: bytes) -> Dict[str, Any]:
        """Analyze audio quality to help with transcription decisions"""
        try:
            # Convert bytes to numpy array for analysis
            # Assume 16-bit signed little-endian PCM
            # Ensure buffer size is even (multiple of 2 bytes for 16-bit samples)
            if len(audio_buffer) % 2 != 0:
                # Remove the last byte if odd length
                audio_buffer = audio_buffer[:-1]
                logger.debug(f"🔧 Trimmed audio buffer to even length: {len(audio_buffer)} bytes")
            
            if len(audio_buffer) == 0:
                return {"is_silence": True, "rms": 0, "clipping_percentage": 0}
            
            audio_data = np.frombuffer(audio_buffer, dtype=np.int16)
            
            # Calculate RMS (Root Mean Square) - indicates volume level
            rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
            
            # Detect clipping (values at or near maximum/minimum)
            max_val = np.max(np.abs(audio_data))
            clipping_threshold = 0.95 * 32767  # 95% of max 16-bit value
            clipped_samples = np.sum(np.abs(audio_data) > clipping_threshold)
            clipping_percentage = (clipped_samples / len(audio_data)) * 100
            
            # Detect silence (very low RMS)
            silence_threshold = 100  # Adjust based on testing
            is_silence = rms < silence_threshold
            
            # Detect noise (high frequency content without clear speech patterns)
            # Simple heuristic: check for consistent patterns vs random noise
            if len(audio_data) > 1000:
                # Calculate spectral characteristics
                fft = np.fft.fft(audio_data[:1000])  # Use first 1000 samples
                freqs = np.fft.fftfreq(1000)
                power_spectrum = np.abs(fft) ** 2
                
                # Check for speech-like frequency distribution (rough heuristic)
                speech_freq_range = (freqs >= 0.1) & (freqs <= 0.4)  # Roughly 1.6-6.4 kHz at 16kHz sample rate
                speech_power = np.sum(power_spectrum[speech_freq_range])
                total_power = np.sum(power_spectrum[freqs > 0])
                
                speech_ratio = speech_power / total_power if total_power > 0 else 0
                is_likely_speech = speech_ratio > 0.1  # At least 10% power in speech range
            else:
                is_likely_speech = True  # Assume speech for short samples
            
            return {
                "is_silence": is_silence,
                "rms": float(rms),
                "clipping_percentage": float(clipping_percentage),
                "max_amplitude": int(max_val),
                "is_likely_speech": is_likely_speech,
                "sample_count": len(audio_data)
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Audio quality analysis failed: {e}")
            return {"is_silence": False, "rms": 0, "clipping_percentage": 0}

# Global service instance
_deepgram_service = None

def get_deepgram_service() -> DeepgramService:
    """Get or create the global Deepgram service instance"""
    global _deepgram_service
    if _deepgram_service is None:
        _deepgram_service = DeepgramService()
    return _deepgram_service
