"""
Audio Player Routes for Convonet Project
Integrated audio player functionality for the main Flask app
"""

import base64
import json
import time
import tempfile
import os
from flask import Blueprint, render_template, request, jsonify, Response
from flask_socketio import emit

# Redis imports
try:
    from convonet.redis_manager import redis_manager, get_session
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis not available")

# Create blueprint
audio_player_bp = Blueprint('audio_player', __name__, url_prefix='/audio-player')

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
                    'has_audio': len(audio_buffer) > 0,
                    'connected_at': session_data.get('connected_at', ''),
                    'authenticated_at': session_data.get('authenticated_at', '')
                })
        
        return sessions
    except Exception as e:
        print(f"❌ Error getting sessions: {e}")
        return []

def create_wav_file(audio_data):
    """Create WAV file from raw audio data"""
    import wave
    
    # Try different audio parameters
    audio_params = [
        {"channels": 1, "sample_width": 2, "framerate": 44100, "desc": "16-bit, 44.1kHz, mono"},
        {"channels": 1, "sample_width": 2, "framerate": 16000, "desc": "16-bit, 16kHz, mono"},
        {"channels": 1, "sample_width": 1, "framerate": 44100, "desc": "8-bit, 44.1kHz, mono"},
        {"channels": 2, "sample_width": 2, "framerate": 44100, "desc": "16-bit, 44.1kHz, stereo"},
    ]
    
    for params in audio_params:
        temp_file = None
        try:
            # Create temporary WAV file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(params['channels'])
                wav_file.setsampwidth(params['sample_width'])
                wav_file.setframerate(params['framerate'])
                wav_file.writeframes(audio_data)
            
            print(f"✅ Created WAV file with {params['desc']}")
            return temp_file.name, params['desc']
            
        except Exception as e:
            print(f"❌ Failed with {params['desc']}: {e}")
            if temp_file and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            continue
    
    return None, "All audio parameter combinations failed"

@audio_player_bp.route('/')
def index():
    """Main audio player page"""
    return render_template('audio_player_dashboard.html')

@audio_player_bp.route('/api/sessions')
def api_sessions():
    """Get list of active sessions"""
    sessions = get_active_sessions()
    return jsonify({
        'success': True,
        'sessions': sessions,
        'redis_available': REDIS_AVAILABLE
    })

@audio_player_bp.route('/api/session/<session_id>/info')
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

@audio_player_bp.route('/api/session/<session_id>/download')
def api_download_audio(session_id):
    """Download audio as WAV file"""
    try:
        if not REDIS_AVAILABLE:
            return jsonify({'success': False, 'message': 'Redis not available'})
        
        # Get session data
        session_data = get_session(session_id)
        if not session_data:
            return jsonify({'success': False, 'message': 'Session not found'})
        
        # Get audio buffer
        audio_buffer_b64 = session_data.get('audio_buffer', '')
        if not audio_buffer_b64:
            return jsonify({'success': False, 'message': 'No audio buffer found'})
        
        # Decode audio data
        try:
            audio_data = base64.b64decode(audio_buffer_b64)
        except Exception as e:
            return jsonify({'success': False, 'message': f'Failed to decode audio: {e}'})
        
        # Check if audio is WebM format (from WebRTC)
        if audio_data.startswith(b'\x1a\x45\xdf\xa3'):  # WebM/Matroska header
            # For WebM, return the original file without conversion
            def generate():
                yield audio_data
            
            return Response(
                generate(),
                mimetype='audio/webm',
                headers={
                    'Content-Disposition': f'attachment; filename="session_{session_id}_audio.webm"',
                    'Content-Type': 'audio/webm'
                }
            )
        else:
            # For other formats, create WAV file
            wav_file_path, format_desc = create_wav_file(audio_data)
            if not wav_file_path:
                return jsonify({'success': False, 'message': f'Failed to create WAV file: {format_desc}'})
            
            # Return WAV file
            def generate():
                with open(wav_file_path, 'rb') as f:
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        yield data
                # Clean up
                os.unlink(wav_file_path)
            
            return Response(
                generate(),
                mimetype='audio/wav',
                headers={
                    'Content-Disposition': f'attachment; filename=audio_{session_id}.wav'
                }
            )
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {e}'})

@audio_player_bp.route('/api/session/<session_id>/analyze')
def api_analyze_audio(session_id):
    """Analyze audio buffer in detail"""
    try:
        if not REDIS_AVAILABLE:
            return jsonify({'success': False, 'message': 'Redis not available'})
        
        # Get session data
        session_data = get_session(session_id)
        if not session_data:
            return jsonify({'success': False, 'message': 'Session not found'})
        
        # Get audio buffer
        audio_buffer_b64 = session_data.get('audio_buffer', '')
        if not audio_buffer_b64:
            return jsonify({'success': False, 'message': 'No audio buffer found'})
        
        # Decode audio data
        try:
            audio_data = base64.b64decode(audio_buffer_b64)
        except Exception as e:
            return jsonify({'success': False, 'message': f'Failed to decode audio: {e}'})
        
        # Analyze audio data
        analysis = {
            'base64_length': len(audio_buffer_b64),
            'decoded_length': len(audio_data),
            'first_20_bytes_hex': audio_data[:20].hex(),
            'first_20_bytes_chars': str(audio_data[:20]),
            'null_bytes_count': audio_data.count(b'\x00'),
            'null_bytes_percentage': (audio_data.count(b'\x00') / len(audio_data)) * 100 if audio_data else 0,
            'unique_bytes': len(set(audio_data[:100])) if len(audio_data) >= 100 else len(set(audio_data)),
            'has_repetitive_pattern': len(set(audio_data[:100])) < 10 if len(audio_data) >= 100 else False
        }
        
        # Check for audio headers
        headers = {
            'riff_wav': audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:12],
            'id3_mp3': audio_data.startswith(b'ID3'),
            'mp3_sync': audio_data.startswith(b'\xff\xfb'),
            'ogg': audio_data.startswith(b'OggS'),
            'webm': audio_data.startswith(b'\x1a\x45\xdf\xa3'),
            'mp4_m4a': audio_data.startswith(b'ftyp')
        }
        
        analysis['headers'] = headers
        analysis['detected_format'] = 'Unknown'
        
        for format_name, detected in headers.items():
            if detected:
                analysis['detected_format'] = format_name
                break
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {e}'})
