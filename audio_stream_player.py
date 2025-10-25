#!/usr/bin/env python3
"""
Audio Stream Player for Sambanova Project
Plays audio streams from Redis audio buffers
"""

import base64
import json
import time
import wave
import tempfile
import os
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
import threading
import queue

# Redis imports
try:
    from sambanova.redis_manager import redis_manager, get_session
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis not available")

# Audio processing imports
try:
    import pyaudio
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ PyAudio not available - install with: pip install pyaudio")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'audio_stream_player_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global audio player state
audio_players = {}
audio_queue = queue.Queue()

class AudioStreamPlayer:
    """Audio stream player for Redis audio buffers"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.is_playing = False
        self.audio_data = None
        self.temp_file = None
        self.audio_thread = None
        
    def load_audio_from_redis(self):
        """Load audio data from Redis session"""
        if not REDIS_AVAILABLE:
            return False, "Redis not available"
        
        try:
            session_data = get_session(self.session_id)
            if not session_data:
                return False, "Session not found"
            
            audio_buffer_b64 = session_data.get('audio_buffer', '')
            if not audio_buffer_b64:
                return False, "No audio buffer found"
            
            # Decode base64 audio data
            try:
                self.audio_data = base64.b64decode(audio_buffer_b64)
                return True, f"Audio loaded: {len(self.audio_data)} bytes"
            except Exception as e:
                return False, f"Failed to decode audio: {e}"
                
        except Exception as e:
            return False, f"Redis error: {e}"
    
    def create_wav_file(self):
        """Create WAV file from audio data"""
        if not self.audio_data:
            return False, "No audio data"
        
        try:
            # Create temporary WAV file
            self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            
            # Try different audio parameters
            audio_params = [
                {"channels": 1, "sample_width": 2, "framerate": 44100, "desc": "16-bit, 44.1kHz, mono"},
                {"channels": 1, "sample_width": 2, "framerate": 16000, "desc": "16-bit, 16kHz, mono"},
                {"channels": 1, "sample_width": 1, "framerate": 44100, "desc": "8-bit, 44.1kHz, mono"},
                {"channels": 2, "sample_width": 2, "framerate": 44100, "desc": "16-bit, 44.1kHz, stereo"},
            ]
            
            for params in audio_params:
                try:
                    with wave.open(self.temp_file.name, 'wb') as wav_file:
                        wav_file.setnchannels(params['channels'])
                        wav_file.setsampwidth(params['sample_width'])
                        wav_file.setframerate(params['framerate'])
                        wav_file.writeframes(self.audio_data)
                    
                    print(f"✅ Created WAV file with {params['desc']}")
                    return True, f"WAV created with {params['desc']}"
                    
                except Exception as e:
                    print(f"❌ Failed with {params['desc']}: {e}")
                    continue
            
            return False, "All audio parameter combinations failed"
            
        except Exception as e:
            return False, f"Failed to create WAV file: {e}"
    
    def play_audio(self):
        """Play audio using PyAudio"""
        if not AUDIO_AVAILABLE:
            return False, "PyAudio not available"
        
        if not self.temp_file or not os.path.exists(self.temp_file.name):
            return False, "No WAV file available"
        
        try:
            # Read WAV file
            with wave.open(self.temp_file.name, 'rb') as wav_file:
                # Get audio parameters
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                frames = wav_file.getnframes()
                
                print(f"🎵 Playing audio: {channels} channels, {sample_width} bytes/sample, {framerate} Hz, {frames} frames")
                
                # Initialize PyAudio
                p = pyaudio.PyAudio()
                
                # Open audio stream
                stream = p.open(
                    format=p.get_format_from_width(sample_width),
                    channels=channels,
                    rate=framerate,
                    output=True
                )
                
                # Play audio in chunks
                chunk_size = 1024
                self.is_playing = True
                
                # Read and play audio data
                while self.is_playing:
                    data = wav_file.readframes(chunk_size)
                    if not data:
                        break
                    stream.write(data)
                
                # Clean up
                stream.stop_stream()
                stream.close()
                p.terminate()
                
                self.is_playing = False
                return True, "Audio playback completed"
                
        except Exception as e:
            self.is_playing = False
            return False, f"Playback error: {e}"
    
    def stop_audio(self):
        """Stop audio playback"""
        self.is_playing = False
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_audio()
        if self.temp_file and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
            self.temp_file = None

def get_active_sessions():
    """Get list of active sessions from Redis"""
    if not REDIS_AVAILABLE:
        return []
    
    try:
        session_keys = redis_manager.redis_client.keys("session:*")
        sessions = []
        
        for key in session_keys:
            session_id = key.replace("session:", "")
            session_data = redis_manager.redis_client.hgetall(key)
            
            if session_data:
                audio_buffer = session_data.get('audio_buffer', '')
                sessions.append({
                    'session_id': session_id,
                    'user_name': session_data.get('user_name', 'Unknown'),
                    'authenticated': session_data.get('authenticated', 'False'),
                    'is_recording': session_data.get('is_recording', 'False'),
                    'audio_buffer_length': len(audio_buffer),
                    'has_audio': len(audio_buffer) > 0
                })
        
        return sessions
    except Exception as e:
        print(f"❌ Error getting sessions: {e}")
        return []

@app.route('/')
def index():
    """Main page"""
    return render_template('audio_player.html')

@app.route('/api/sessions')
def api_sessions():
    """Get list of active sessions"""
    sessions = get_active_sessions()
    return jsonify({
        'success': True,
        'sessions': sessions,
        'redis_available': REDIS_AVAILABLE,
        'audio_available': AUDIO_AVAILABLE
    })

@app.route('/api/session/<session_id>/info')
def api_session_info(session_id):
    """Get detailed session information"""
    if not REDIS_AVAILABLE:
        return jsonify({'success': False, 'message': 'Redis not available'})
    
    try:
        session_data = get_session(session_id)
        if not session_data:
            return jsonify({'success': False, 'message': 'Session not found'})
        
        # Analyze audio buffer
        audio_buffer = session_data.get('audio_buffer', '')
        audio_info = {
            'length': len(audio_buffer),
            'has_audio': len(audio_buffer) > 0,
            'preview': audio_buffer[:100] + "..." if len(audio_buffer) > 100 else audio_buffer
        }
        
        # Test base64 decoding
        try:
            if audio_buffer:
                decoded = base64.b64decode(audio_buffer)
                audio_info['decoded_length'] = len(decoded)
                audio_info['base64_valid'] = True
            else:
                audio_info['decoded_length'] = 0
                audio_info['base64_valid'] = True
        except Exception as e:
            audio_info['base64_valid'] = False
            audio_info['base64_error'] = str(e)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'data': session_data,
            'audio_info': audio_info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {e}'})

@app.route('/api/session/<session_id>/play', methods=['POST'])
def api_play_audio(session_id):
    """Play audio from session"""
    try:
        # Create audio player
        player = AudioStreamPlayer(session_id)
        audio_players[session_id] = player
        
        # Load audio from Redis
        success, message = player.load_audio_from_redis()
        if not success:
            return jsonify({'success': False, 'message': message})
        
        # Create WAV file
        success, message = player.create_wav_file()
        if not success:
            return jsonify({'success': False, 'message': message})
        
        # Start playback in background thread
        def play_thread():
            try:
                success, message = player.play_audio()
                socketio.emit('playback_complete', {
                    'session_id': session_id,
                    'success': success,
                    'message': message
                })
            except Exception as e:
                socketio.emit('playback_error', {
                    'session_id': session_id,
                    'error': str(e)
                })
            finally:
                player.cleanup()
                if session_id in audio_players:
                    del audio_players[session_id]
        
        thread = threading.Thread(target=play_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Audio playback started',
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {e}'})

@app.route('/api/session/<session_id>/stop', methods=['POST'])
def api_stop_audio(session_id):
    """Stop audio playback"""
    try:
        if session_id in audio_players:
            audio_players[session_id].stop_audio()
            return jsonify({'success': True, 'message': 'Audio stopped'})
        else:
            return jsonify({'success': False, 'message': 'No active playback'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {e}'})

@app.route('/api/session/<session_id>/download')
def api_download_audio(session_id):
    """Download audio as WAV file"""
    try:
        player = AudioStreamPlayer(session_id)
        
        # Load audio from Redis
        success, message = player.load_audio_from_redis()
        if not success:
            return jsonify({'success': False, 'message': message})
        
        # Create WAV file
        success, message = player.create_wav_file()
        if not success:
            return jsonify({'success': False, 'message': message})
        
        # Return WAV file
        def generate():
            with open(player.temp_file.name, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    yield data
        
        return Response(
            generate(),
            mimetype='audio/wav',
            headers={
                'Content-Disposition': f'attachment; filename=audio_{session_id}.wav'
            }
        )
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {e}'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"✅ Audio player client connected: {request.sid}")
    emit('connected', {'message': 'Connected to audio stream player'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"❌ Audio player client disconnected: {request.sid}")

if __name__ == '__main__':
    print("🎵 Audio Stream Player for Sambanova Project")
    print(f"Redis Available: {REDIS_AVAILABLE}")
    print(f"Audio Available: {AUDIO_AVAILABLE}")
    
    if not REDIS_AVAILABLE:
        print("⚠️ Redis not available - some features will be limited")
    
    if not AUDIO_AVAILABLE:
        print("⚠️ PyAudio not available - install with: pip install pyaudio")
    
    # Run the application
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
