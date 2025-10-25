"""
WebRTC Voice Assistant Server
Provides high-quality audio streaming and real-time speech recognition
"""

import asyncio
import json
import os
import base64
import time
from flask import Blueprint, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import openai
from sambanova.assistant_graph_todo import get_agent
from sambanova.state import AgentState
from langchain_core.messages import HumanMessage

# Sentry integration for monitoring Redis interactions and errors
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.socketio import SocketIOIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
# Optional Redis imports - app should work without them
try:
    from sambanova.redis_manager import redis_manager, create_session, get_session, update_session, delete_session
    REDIS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Redis not available: {e}")
    REDIS_AVAILABLE = False
    # Create dummy functions for fallback
    class DummyRedisManager:
        def is_available(self):
            return False
    redis_manager = DummyRedisManager()
    def create_session(*args, **kwargs):
        return False
    def get_session(*args, **kwargs):
        return None
    def update_session(*args, **kwargs):
        return False
    def delete_session(*args, **kwargs):
        return False

webrtc_bp = Blueprint('webrtc_voice', __name__, url_prefix='/sambanova_todo/webrtc')

# Initialize OpenAI client for Whisper and TTS
openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Active sessions storage (fallback for when Redis is unavailable)
active_sessions = {}

# Global references for background tasks
socketio = None
flask_app = None

# Sentry helper functions
def sentry_capture_redis_operation(operation: str, session_id: str, success: bool, error: str = None):
    """Capture Redis operations in Sentry for monitoring"""
    if SENTRY_AVAILABLE:
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("component", "webrtc_voice_server")
            scope.set_tag("operation", f"redis_{operation}")
            scope.set_context("redis_operation", {
                "session_id": session_id,
                "operation": operation,
                "success": success,
                "error": error
            })
            if success:
                sentry_sdk.add_breadcrumb(
                    message=f"Redis {operation} successful",
                    category="redis",
                    level="info"
                )
            else:
                sentry_sdk.capture_message(f"Redis {operation} failed: {error}", level="error")

def sentry_capture_voice_event(event: str, session_id: str, user_id: str = None, details: dict = None):
    """Capture voice assistant events in Sentry"""
    if SENTRY_AVAILABLE:
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("component", "webrtc_voice_server")
            scope.set_tag("event", event)
            scope.set_context("voice_event", {
                "session_id": session_id,
                "user_id": user_id,
                "event": event,
                "details": details or {}
            })
            sentry_sdk.add_breadcrumb(
                message=f"Voice event: {event}",
                category="voice_assistant",
                level="info"
            )


@webrtc_bp.route('/voice-assistant')
def voice_assistant():
    """Render the WebRTC voice assistant interface"""
    return render_template('webrtc_voice_assistant.html')


@webrtc_bp.route('/debug-session/<session_id>')
def debug_session(session_id):
    """Debug endpoint to check Redis session data"""
    try:
        if redis_manager.is_available():
            session_data = get_session(session_id)
            if session_data:
                # Convert bytes to strings for JSON serialization
                debug_data = {}
                for key, value in session_data.items():
                    if isinstance(value, bytes):
                        debug_data[key] = value.decode('utf-8', errors='ignore')
                    else:
                        debug_data[key] = str(value)
                
                # Add audio buffer info
                audio_buffer = session_data.get('audio_buffer', '')
                debug_data['audio_buffer_length'] = len(audio_buffer)
                debug_data['audio_buffer_preview'] = audio_buffer[:100] + "..." if len(audio_buffer) > 100 else audio_buffer
                
                # Test base64 decoding
                try:
                    if audio_buffer:
                        decoded = base64.b64decode(audio_buffer)
                        debug_data['decoded_audio_length'] = len(decoded)
                        debug_data['base64_valid'] = True
                    else:
                        debug_data['decoded_audio_length'] = 0
                        debug_data['base64_valid'] = True
                except Exception as e:
                    debug_data['base64_valid'] = False
                    debug_data['base64_error'] = str(e)
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'data': debug_data,
                    'storage': 'redis'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Session not found in Redis',
                    'session_id': session_id
                })
        else:
            # Check in-memory storage
            if session_id in active_sessions:
                session_data = active_sessions[session_id]
                debug_data = {
                    'authenticated': session_data.get('authenticated', False),
                    'user_id': session_data.get('user_id'),
                    'user_name': session_data.get('user_name'),
                    'is_recording': session_data.get('is_recording', False),
                    'audio_buffer_length': len(session_data.get('audio_buffer', b'')),
                    'storage': 'memory'
                }
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'data': debug_data,
                    'storage': 'memory'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Session not found in memory',
                    'session_id': session_id
                })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'session_id': session_id
        })


@webrtc_bp.route('/clear-session/<session_id>')
def clear_session(session_id):
    """Clear Redis session data for testing"""
    try:
        if redis_manager.is_available():
            # Clear the session
            delete_session(session_id)
            return jsonify({
                'success': True,
                'message': f'Session {session_id} cleared from Redis'
            })
        else:
            # Clear from memory
            if session_id in active_sessions:
                del active_sessions[session_id]
                return jsonify({
                    'success': True,
                    'message': f'Session {session_id} cleared from memory'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Session {session_id} not found'
                })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'session_id': session_id
        })


def init_socketio(socketio_instance: SocketIO, app):
    """Initialize Socket.IO event handlers"""
    
    # Store socketio instance and Flask app for background tasks
    global socketio, flask_app
    socketio = socketio_instance
    flask_app = app  # Store Flask app directly (passed as parameter)
    
    @socketio.on('connect', namespace='/voice')
    def handle_connect():
        """Handle client connection"""
        session_id = request.sid
        print(f"✅ WebRTC client connected: {session_id}")
        
        # Capture connection event in Sentry
        sentry_capture_voice_event("client_connected", session_id)
        
        # Initialize session in Redis (with fallback to in-memory)
        session_data = {
            'authenticated': 'False',
            'user_id': '',
            'user_name': '',
            'audio_buffer': '',
            'is_recording': 'False',
            'connected_at': str(time.time())
        }
        
        try:
            if redis_manager.is_available():
                success = create_session(session_id, session_data, ttl=3600)  # 1 hour TTL
                if success:
                    print(f"✅ Session stored in Redis: {session_id}")
                    sentry_capture_redis_operation("create_session", session_id, True)
                else:
                    print(f"❌ Failed to store session in Redis: {session_id}")
                    sentry_capture_redis_operation("create_session", session_id, False, "Redis create_session returned False")
            else:
                # Fallback to in-memory storage
                active_sessions[session_id] = {
                    'authenticated': False,
                    'user_id': None,
                    'user_name': None,
                    'audio_buffer': b'',
                    'is_recording': False
                }
                print(f"⚠️ Using in-memory storage (Redis unavailable): {session_id}")
                sentry_capture_voice_event("redis_fallback", session_id, details={"storage": "in_memory"})
        except Exception as e:
            print(f"❌ Error creating session: {e}")
            sentry_capture_redis_operation("create_session", session_id, False, str(e))
            # Fallback to in-memory storage on error
            active_sessions[session_id] = {
                'authenticated': False,
                'user_id': None,
                'user_name': None,
                'audio_buffer': b'',
                'is_recording': False
            }
        
        emit('connected', {'session_id': session_id})
    
    
    @socketio.on('disconnect', namespace='/voice')
    def handle_disconnect():
        """Handle client disconnection"""
        session_id = request.sid
        print(f"❌ WebRTC client disconnected: {session_id}")
        
        # Capture disconnection event in Sentry
        sentry_capture_voice_event("client_disconnected", session_id)
        
        try:
            if redis_manager.is_available():
                success = delete_session(session_id)
                if success:
                    print(f"✅ Session deleted from Redis: {session_id}")
                    sentry_capture_redis_operation("delete_session", session_id, True)
                else:
                    print(f"❌ Failed to delete session from Redis: {session_id}")
                    sentry_capture_redis_operation("delete_session", session_id, False, "Redis delete_session returned False")
            else:
                if session_id in active_sessions:
                    del active_sessions[session_id]
                    print(f"✅ Session deleted from memory: {session_id}")
                    sentry_capture_voice_event("session_deleted_memory", session_id)
        except Exception as e:
            print(f"❌ Error deleting session: {e}")
            sentry_capture_redis_operation("delete_session", session_id, False, str(e))
    
    
    @socketio.on('authenticate', namespace='/voice')
    def handle_authenticate(data):
        """Handle user authentication"""
        session_id = request.sid
        pin = data.get('pin', '')
        
        print(f"🔐 Authentication request for session {session_id}: PIN={pin}")
        
        # Capture authentication attempt in Sentry
        sentry_capture_voice_event("authentication_attempt", session_id, details={"pin_provided": bool(pin)})
        
        try:
            # Import here to avoid circular imports
            from sambanova.mcps.local_servers.db_todo import _init_database, SessionLocal
            from sambanova.models.user_models import User as UserModel
            
            _init_database()
            
            with SessionLocal() as db_session:
                user = db_session.query(UserModel).filter(
                    UserModel.voice_pin == pin,
                    UserModel.is_active == True
                ).first()
                
                if user:
                    # Authentication successful
                    auth_updates = {
                        'authenticated': 'True',
                        'user_id': str(user.id),
                        'user_name': user.first_name,
                        'authenticated_at': str(time.time())
                    }
                    
                    try:
                        if redis_manager.is_available():
                            success = update_session(session_id, auth_updates)
                            if success:
                                print(f"✅ Authentication stored in Redis: {user.email}")
                                sentry_capture_redis_operation("update_session", session_id, True)
                                sentry_capture_voice_event("authentication_success", session_id, str(user.id), {"user_name": user.first_name, "storage": "redis"})
                            else:
                                print(f"❌ Failed to update session in Redis: {user.email}")
                                sentry_capture_redis_operation("update_session", session_id, False, "Redis update_session returned False")
                                # Fallback to in-memory
                                active_sessions[session_id]['authenticated'] = True
                                active_sessions[session_id]['user_id'] = str(user.id)
                                active_sessions[session_id]['user_name'] = user.first_name
                                print(f"✅ Authentication stored in memory (Redis fallback): {user.email}")
                                sentry_capture_voice_event("authentication_success", session_id, str(user.id), {"user_name": user.first_name, "storage": "memory_fallback"})
                        else:
                            # Fallback to in-memory
                            active_sessions[session_id]['authenticated'] = True
                            active_sessions[session_id]['user_id'] = str(user.id)
                            active_sessions[session_id]['user_name'] = user.first_name
                            print(f"✅ Authentication stored in memory: {user.email}")
                            sentry_capture_voice_event("authentication_success", session_id, str(user.id), {"user_name": user.first_name, "storage": "memory"})
                    except Exception as redis_error:
                        print(f"❌ Redis error during authentication: {redis_error}")
                        sentry_capture_redis_operation("update_session", session_id, False, str(redis_error))
                        # Fallback to in-memory storage
                        active_sessions[session_id]['authenticated'] = True
                        active_sessions[session_id]['user_id'] = str(user.id)
                        active_sessions[session_id]['user_name'] = user.first_name
                        print(f"✅ Authentication stored in memory (Redis error fallback): {user.email}")
                        sentry_capture_voice_event("authentication_success", session_id, str(user.id), {"user_name": user.first_name, "storage": "memory_error_fallback"})
                    
                    emit('authenticated', {
                        'success': True,
                        'user_name': user.first_name,
                        'message': f"Welcome back, {user.first_name}!"
                    })
                    
                    # Send welcome greeting with audio (background task)
                    socketio.start_background_task(
                        send_welcome_greeting, 
                        session_id, 
                        user.first_name
                    )
                else:
                    # Authentication failed
                    print(f"❌ Authentication failed: Invalid PIN")
                    sentry_capture_voice_event("authentication_failed", session_id, details={"reason": "invalid_pin"})
                    emit('authenticated', {
                        'success': False,
                        'message': "Invalid PIN. Please try again."
                    })
        
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            sentry_capture_voice_event("authentication_error", session_id, details={"error": str(e)})
            if SENTRY_AVAILABLE:
                sentry_sdk.capture_exception(e)
            emit('authenticated', {
                'success': False,
                'message': "Authentication error. Please try again."
            })
    
    
    @socketio.on('start_recording', namespace='/voice')
    def handle_start_recording():
        """Start audio recording"""
        session_id = request.sid
        
        # Get session data
        session_data = None
        if redis_manager.is_available():
            session_data = get_session(session_id)
            if not session_data:
                emit('error', {'message': 'Session not found'})
                return
        else:
            if session_id not in active_sessions:
                emit('error', {'message': 'Session not found'})
                return
            session_data = active_sessions[session_id]
        
        # Check authentication
        is_authenticated = session_data.get('authenticated') == 'True' if redis_manager.is_available() else session_data.get('authenticated', False)
        if not is_authenticated:
            emit('error', {'message': 'Please authenticate first'})
            return
        
        print(f"🎤 Recording started: {session_id}")
        
        # Update recording state
        if redis_manager.is_available():
            update_session(session_id, {
                'is_recording': 'True',
                'audio_buffer': ''  # Start with empty string for base64 concatenation
            })
        else:
            active_sessions[session_id]['is_recording'] = True
            active_sessions[session_id]['audio_buffer'] = b''  # Start with empty bytes for binary concatenation
        
        emit('recording_started', {'success': True})
    
    
    @socketio.on('audio_data', namespace='/voice')
    def handle_audio_data(data):
        """Receive audio data chunks from client"""
        session_id = request.sid
        
        # Get session data
        session_data = None
        if redis_manager.is_available():
            session_data = get_session(session_id)
            if not session_data:
                sentry_capture_voice_event("session_not_found", session_id, details={"operation": "audio_data"})
                return
        else:
            if session_id not in active_sessions:
                sentry_capture_voice_event("session_not_found", session_id, details={"operation": "audio_data", "storage": "memory"})
                return
            session_data = active_sessions[session_id]
        
        # Check if recording
        is_recording = session_data.get('is_recording') == 'True' if redis_manager.is_available() else session_data.get('is_recording', False)
        if not is_recording:
            sentry_capture_voice_event("audio_received_not_recording", session_id, details={"is_recording": is_recording})
            return
        
        # Append audio chunk to buffer
        audio_chunk = base64.b64decode(data['audio'])
        print(f"🔍 Debug: received audio chunk: {len(audio_chunk)} bytes")
        
        try:
            if redis_manager.is_available():
                # For Redis, we need to handle binary data differently
                # Store as base64 string in Redis
                current_buffer = session_data.get('audio_buffer', '')
                new_chunk_b64 = base64.b64encode(audio_chunk).decode('utf-8')
                
                # Validate current buffer is valid base64
                if current_buffer:
                    try:
                        # Test if current buffer is valid base64
                        base64.b64decode(current_buffer)
                        print(f"🔍 Debug: current buffer is valid base64, length: {len(current_buffer)}")
                    except Exception as e:
                        print(f"⚠️ Current buffer is not valid base64, resetting: {e}")
                        current_buffer = ''  # Reset if corrupted
                
                updated_buffer = current_buffer + new_chunk_b64
                
                # Validate the updated buffer
                try:
                    test_decode = base64.b64decode(updated_buffer)
                    print(f"🔍 Debug: updated buffer is valid base64, decoded length: {len(test_decode)}")
                except Exception as e:
                    print(f"❌ Updated buffer is not valid base64: {e}")
                    # Use only the new chunk if concatenation failed
                    updated_buffer = new_chunk_b64
                    print(f"🔍 Debug: using only new chunk, length: {len(updated_buffer)}")
                
                # Use Redis append operation for better performance
                try:
                    # Get the Redis client directly for append operation
                    redis_client = redis_manager.redis_client
                    if redis_client:
                        # Use Redis HSET to update the audio buffer
                        redis_client.hset(f"session:{session_id}", "audio_buffer", updated_buffer)
                        print(f"🔍 Debug: updated Redis audio buffer: {len(updated_buffer)} chars")
                        sentry_capture_redis_operation("update_audio_buffer", session_id, True)
                    else:
                        # Fallback to update_session method
                        success = update_session(session_id, {'audio_buffer': updated_buffer})
                        if success:
                            print(f"🔍 Debug: updated Redis audio buffer (fallback): {len(updated_buffer)} chars")
                            sentry_capture_redis_operation("update_audio_buffer", session_id, True)
                        else:
                            print(f"❌ Failed to update Redis audio buffer")
                            sentry_capture_redis_operation("update_audio_buffer", session_id, False, "Redis update_session returned False")
                except Exception as redis_error:
                    print(f"❌ Redis direct operation failed: {redis_error}")
                    # Fallback to update_session method
                    success = update_session(session_id, {'audio_buffer': updated_buffer})
                    if success:
                        print(f"🔍 Debug: updated Redis audio buffer (error fallback): {len(updated_buffer)} chars")
                        sentry_capture_redis_operation("update_audio_buffer", session_id, True)
                    else:
                        print(f"❌ Failed to update Redis audio buffer (error fallback)")
                        sentry_capture_redis_operation("update_audio_buffer", session_id, False, f"Redis error: {redis_error}")
            else:
                # In-memory storage
                active_sessions[session_id]['audio_buffer'] += audio_chunk
                print(f"🔍 Debug: updated in-memory audio buffer: {len(active_sessions[session_id]['audio_buffer'])} bytes")
                sentry_capture_voice_event("audio_buffer_updated", session_id, details={"storage": "memory", "buffer_size": len(active_sessions[session_id]['audio_buffer'])})
        except Exception as e:
            print(f"❌ Error updating audio buffer: {e}")
            sentry_capture_redis_operation("update_audio_buffer", session_id, False, str(e))
            if SENTRY_AVAILABLE:
                sentry_sdk.capture_exception(e)
    
    
    @socketio.on('stop_recording', namespace='/voice')
    def handle_stop_recording():
        """Stop recording and process audio"""
        session_id = request.sid
        
        # Capture stop recording event in Sentry
        sentry_capture_voice_event("stop_recording", session_id)
        
        # Get session data
        session_data = None
        if redis_manager.is_available():
            session_data = get_session(session_id)
            if not session_data:
                sentry_capture_voice_event("session_not_found", session_id, details={"operation": "stop_recording"})
                emit('error', {'message': 'Session not found'})
                return
        else:
            if session_id not in active_sessions:
                sentry_capture_voice_event("session_not_found", session_id, details={"operation": "stop_recording", "storage": "memory"})
                emit('error', {'message': 'Session not found'})
                return
            session_data = active_sessions[session_id]
        
        # Check if recording
        is_recording = session_data.get('is_recording') == 'True' if redis_manager.is_available() else session_data.get('is_recording', False)
        if not is_recording:
            sentry_capture_voice_event("stop_recording_not_recording", session_id, details={"is_recording": is_recording})
            emit('error', {'message': 'Not recording'})
            return
        
        print(f"🛑 Recording stopped: {session_id}")
        
        # Update recording state
        try:
            if redis_manager.is_available():
                success = update_session(session_id, {'is_recording': 'False'})
                if success:
                    sentry_capture_redis_operation("update_recording_state", session_id, True)
                else:
                    sentry_capture_redis_operation("update_recording_state", session_id, False, "Redis update_session returned False")
            else:
                session_data['is_recording'] = False
                sentry_capture_voice_event("recording_state_updated", session_id, details={"storage": "memory"})
        except Exception as e:
            print(f"❌ Error updating recording state: {e}")
            sentry_capture_redis_operation("update_recording_state", session_id, False, str(e))
        
        # Get audio buffer
        try:
            if redis_manager.is_available():
                # Decode base64 string back to binary
                audio_buffer_b64 = session_data.get('audio_buffer', '')
                print(f"🔍 Debug: audio_buffer_b64 length: {len(audio_buffer_b64)}")
                print(f"🔍 Debug: audio_buffer_b64 preview: {audio_buffer_b64[:100]}..." if len(audio_buffer_b64) > 100 else f"🔍 Debug: audio_buffer_b64 full: {audio_buffer_b64}")
                
                if not audio_buffer_b64:
                    print("❌ No audio data in Redis session")
                    print(f"🔍 Debug: Full session data: {session_data}")
                    sentry_capture_voice_event("no_audio_data", session_id, details={"storage": "redis", "session_data": session_data})
                    emit('transcription', {
                        'success': False,
                        'message': 'No audio data received.'
                    })
                    return
                
                try:
                    audio_buffer = base64.b64decode(audio_buffer_b64)
                    print(f"🔍 Debug: decoded audio_buffer length: {len(audio_buffer)}")
                    sentry_capture_voice_event("audio_buffer_retrieved", session_id, details={"storage": "redis", "buffer_size": len(audio_buffer)})
                except Exception as decode_error:
                    print(f"❌ Error decoding audio buffer: {decode_error}")
                    sentry_capture_voice_event("audio_decode_error", session_id, details={"error": str(decode_error), "buffer_preview": audio_buffer_b64[:100]})
                    emit('transcription', {
                        'success': False,
                        'message': 'Error decoding audio data.'
                    })
                    return
            else:
                audio_buffer = session_data['audio_buffer']
                print(f"🔍 Debug: in-memory audio_buffer length: {len(audio_buffer)}")
                sentry_capture_voice_event("audio_buffer_retrieved", session_id, details={"storage": "memory", "buffer_size": len(audio_buffer)})
        except Exception as e:
            print(f"❌ Error retrieving audio buffer: {e}")
            print(f"🔍 Debug: Session data keys: {list(session_data.keys()) if session_data else 'None'}")
            sentry_capture_voice_event("audio_buffer_error", session_id, details={"error": str(e), "session_keys": list(session_data.keys()) if session_data else []})
            if SENTRY_AVAILABLE:
                sentry_sdk.capture_exception(e)
            emit('error', {'message': 'Error retrieving audio data'})
            return
        
        if len(audio_buffer) < 1000:  # Too short
            sentry_capture_voice_event("audio_too_short", session_id, details={"buffer_size": len(audio_buffer), "threshold": 1000})
            emit('transcription', {
                'success': False,
                'message': 'Audio too short. Please try again.'
            })
            return
        
        # Process audio asynchronously
        sentry_capture_voice_event("audio_processing_started", session_id, details={"buffer_size": len(audio_buffer)})
        socketio.start_background_task(process_audio_async, session_id, audio_buffer)
    
    
    def send_welcome_greeting(session_id, user_name):
        """Send welcome greeting with TTS audio after authentication"""
        with flask_app.app_context():
            try:
                print(f"🎤 Generating welcome greeting for {user_name}")
                
                # Generate welcome message
                welcome_text = f"Welcome back, {user_name}! I'm your Sambanova productivity assistant. How can I help you today?"
                
                # Generate TTS audio
                speech_response = openai_client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=welcome_text
                )
                
                # Convert to base64
                audio_base64 = base64.b64encode(speech_response.content).decode('utf-8')
                
                # Send to client
                socketio.emit('welcome_greeting', {
                    'text': welcome_text,
                    'audio': audio_base64
                }, namespace='/voice', room=session_id)
                
                print(f"✅ Welcome greeting sent to {user_name}")
                
            except Exception as e:
                print(f"❌ Error generating welcome greeting: {e}")
    
    
    def process_audio_async(session_id, audio_buffer):
        """Process audio in background task"""
        # Use the stored Flask app instance for application context
        with flask_app.app_context():
            try:
                # Get session data
                session = None
                if redis_manager.is_available():
                    session_data = get_session(session_id)
                    if not session_data:
                        sentry_capture_voice_event("session_not_found_processing", session_id, details={"operation": "audio_processing"})
                        return
                    # Convert Redis session data to expected format
                    session = {
                        'user_id': session_data.get('user_id'),
                        'user_name': session_data.get('user_name')
                    }
                else:
                    session = active_sessions.get(session_id)
                    if not session:
                        sentry_capture_voice_event("session_not_found_processing", session_id, details={"operation": "audio_processing", "storage": "memory"})
                        return
                
                print(f"🎧 Processing audio: {len(audio_buffer)} bytes")
                sentry_capture_voice_event("audio_processing_started", session_id, session.get('user_id'), details={"buffer_size": len(audio_buffer)})
                
                # Step 1: Transcribe audio using OpenAI Whisper
                socketio.emit('status', {'message': 'Transcribing...'}, namespace='/voice', room=session_id)
                sentry_capture_voice_event("transcription_started", session_id, session.get('user_id'))
                
                # Save audio to temporary file (Whisper API requires file)
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_audio:
                    temp_audio.write(audio_buffer)
                    temp_audio_path = temp_audio.name
                
                try:
                    with open(temp_audio_path, 'rb') as audio_file:
                        transcription = openai_client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                            language="en"
                        )
                    
                    transcribed_text = transcription.text
                    print(f"📝 Transcription: {transcribed_text}")
                    sentry_capture_voice_event("transcription_completed", session_id, session.get('user_id'), details={"text_length": len(transcribed_text)})
                    
                    # Send transcription to client
                    socketio.emit('transcription', {
                        'success': True,
                        'text': transcribed_text
                    }, namespace='/voice', room=session_id)
                    
                    # Step 2: Process with agent
                    socketio.emit('status', {'message': 'Processing request...'}, namespace='/voice', room=session_id)
                    sentry_capture_voice_event("agent_processing_started", session_id, session.get('user_id'), details={"transcribed_text": transcribed_text})
                    
                    agent_response = asyncio.run(process_with_agent(
                        transcribed_text,
                        session['user_id'],
                        session['user_name']
                    ))
                    
                    print(f"🤖 Agent response: {agent_response}")
                    sentry_capture_voice_event("agent_processing_completed", session_id, session.get('user_id'), details={"response_length": len(agent_response)})
                    
                    # Step 3: Convert response to speech using OpenAI TTS
                    socketio.emit('status', {'message': 'Generating speech...'}, namespace='/voice', room=session_id)
                    sentry_capture_voice_event("tts_generation_started", session_id, session.get('user_id'))
                    
                    speech_response = openai_client.audio.speech.create(
                        model="tts-1",
                        voice="nova",  # Options: alloy, echo, fable, onyx, nova, shimmer
                        input=agent_response
                    )
                    
                    # Convert speech to base64 for transmission
                    audio_base64 = base64.b64encode(speech_response.content).decode('utf-8')
                    sentry_capture_voice_event("tts_generation_completed", session_id, session.get('user_id'), details={"audio_size": len(audio_base64)})
                    
                    # Send response to client
                    socketio.emit('agent_response', {
                        'success': True,
                        'text': agent_response,
                        'audio': audio_base64
                    }, namespace='/voice', room=session_id)
                    
                    sentry_capture_voice_event("audio_processing_completed", session_id, session.get('user_id'), details={"success": True})
                
                finally:
                    # Clean up temp file
                    import os
                    if os.path.exists(temp_audio_path):
                        os.unlink(temp_audio_path)
            
            except Exception as e:
                print(f"❌ Error processing audio: {e}")
                import traceback
                traceback.print_exc()
                
                sentry_capture_voice_event("audio_processing_error", session_id, session.get('user_id') if 'session' in locals() else None, details={"error": str(e)})
                if SENTRY_AVAILABLE:
                    sentry_sdk.capture_exception(e)
                
                socketio.emit('error', {
                    'message': f"Error processing audio: {str(e)}"
                }, namespace='/voice', room=session_id)


async def process_with_agent(text: str, user_id: str, user_name: str) -> str:
    """Process user input with the agent"""
    try:
        # Capture agent processing start in Sentry
        if SENTRY_AVAILABLE:
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("component", "webrtc_voice_server")
                scope.set_tag("operation", "agent_processing")
                scope.set_context("agent_processing", {
                    "user_id": user_id,
                    "user_name": user_name,
                    "text_length": len(text),
                    "text_preview": text[:100] + "..." if len(text) > 100 else text
                })
                sentry_sdk.add_breadcrumb(
                    message="Agent processing started",
                    category="agent",
                    level="info"
                )
        
        # Import the routes module to use its agent graph initialization
        from sambanova.routes import _get_agent_graph
        
        # Get the agent graph with tools
        graph = await _get_agent_graph()
        
        # Create initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=text)],
            customer_id="webrtc_user",
            authenticated_user_id=user_id,
            authenticated_user_name=user_name,
            is_authenticated=True
        )
        
        # Create config with thread_id for checkpointer
        config = {
            "configurable": {
                "thread_id": f"webrtc_{user_id}_{int(asyncio.get_event_loop().time())}"
            }
        }
        
        # Run agent with timeout
        result = await asyncio.wait_for(
            graph.ainvoke(initial_state, config),
            timeout=30.0
        )
        
        # Extract final message
        if result.get('messages'):
            last_message = result['messages'][-1]
            if hasattr(last_message, 'content'):
                response = last_message.content
                # Capture successful agent processing in Sentry
                if SENTRY_AVAILABLE:
                    sentry_sdk.add_breadcrumb(
                        message="Agent processing completed successfully",
                        category="agent",
                        level="info"
                    )
                return response
        
        # Capture fallback response in Sentry
        if SENTRY_AVAILABLE:
            sentry_sdk.add_breadcrumb(
                message="Agent processing completed with fallback response",
                category="agent",
                level="warning"
            )
        return "I processed your request successfully."
    
    except asyncio.TimeoutError:
        # Capture timeout in Sentry
        if SENTRY_AVAILABLE:
            sentry_sdk.capture_message("Agent processing timeout", level="warning")
        return "I'm sorry, I'm taking too long to process that request. Please try again."
    except Exception as e:
        print(f"❌ Agent error: {e}")
        # Capture agent error in Sentry
        if SENTRY_AVAILABLE:
            sentry_sdk.capture_exception(e)
        return "I'm sorry, I encountered an error. Please try again."

