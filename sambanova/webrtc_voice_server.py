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
from sambanova.redis_manager import redis_manager, create_session, get_session, update_session, delete_session

webrtc_bp = Blueprint('webrtc_voice', __name__, url_prefix='/sambanova_todo/webrtc')

# Initialize OpenAI client for Whisper and TTS
openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Active sessions storage (fallback for when Redis is unavailable)
active_sessions = {}

# Global references for background tasks
socketio = None
flask_app = None


@webrtc_bp.route('/voice-assistant')
def voice_assistant():
    """Render the WebRTC voice assistant interface"""
    return render_template('webrtc_voice_assistant.html')


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
        
        # Initialize session in Redis (with fallback to in-memory)
        session_data = {
            'authenticated': 'False',
            'user_id': '',
            'user_name': '',
            'audio_buffer': '',
            'is_recording': 'False',
            'connected_at': str(time.time())
        }
        
        if redis_manager.is_available():
            create_session(session_id, session_data, ttl=3600)  # 1 hour TTL
            print(f"✅ Session stored in Redis: {session_id}")
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
        
        emit('connected', {'session_id': session_id})
    
    
    @socketio.on('disconnect', namespace='/voice')
    def handle_disconnect():
        """Handle client disconnection"""
        session_id = request.sid
        print(f"❌ WebRTC client disconnected: {session_id}")
        
        if redis_manager.is_available():
            delete_session(session_id)
            print(f"✅ Session deleted from Redis: {session_id}")
        else:
            if session_id in active_sessions:
                del active_sessions[session_id]
                print(f"✅ Session deleted from memory: {session_id}")
    
    
    @socketio.on('authenticate', namespace='/voice')
    def handle_authenticate(data):
        """Handle user authentication"""
        session_id = request.sid
        pin = data.get('pin', '')
        
        print(f"🔐 Authentication request for session {session_id}: PIN={pin}")
        
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
                    
                    if redis_manager.is_available():
                        update_session(session_id, auth_updates)
                        print(f"✅ Authentication stored in Redis: {user.email}")
                    else:
                        # Fallback to in-memory
                        active_sessions[session_id]['authenticated'] = True
                        active_sessions[session_id]['user_id'] = str(user.id)
                        active_sessions[session_id]['user_name'] = user.first_name
                        print(f"✅ Authentication stored in memory: {user.email}")
                    
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
                    emit('authenticated', {
                        'success': False,
                        'message': "Invalid PIN. Please try again."
                    })
        
        except Exception as e:
            print(f"❌ Authentication error: {e}")
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
                'audio_buffer': ''
            })
        else:
            active_sessions[session_id]['is_recording'] = True
            active_sessions[session_id]['audio_buffer'] = b''
        
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
                return
        else:
            if session_id not in active_sessions:
                return
            session_data = active_sessions[session_id]
        
        # Check if recording
        is_recording = session_data.get('is_recording') == 'True' if redis_manager.is_available() else session_data.get('is_recording', False)
        if not is_recording:
            return
        
        # Append audio chunk to buffer
        audio_chunk = base64.b64decode(data['audio'])
        
        if redis_manager.is_available():
            # For Redis, we need to handle binary data differently
            # Store as base64 string in Redis
            current_buffer = session_data.get('audio_buffer', '')
            new_chunk_b64 = base64.b64encode(audio_chunk).decode('utf-8')
            updated_buffer = current_buffer + new_chunk_b64
            update_session(session_id, {'audio_buffer': updated_buffer})
        else:
            # In-memory storage
            active_sessions[session_id]['audio_buffer'] += audio_chunk
    
    
    @socketio.on('stop_recording', namespace='/voice')
    def handle_stop_recording():
        """Stop recording and process audio"""
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
        
        # Check if recording
        is_recording = session_data.get('is_recording') == 'True' if redis_manager.is_available() else session_data.get('is_recording', False)
        if not is_recording:
            emit('error', {'message': 'Not recording'})
            return
        
        print(f"🛑 Recording stopped: {session_id}")
        
        # Update recording state
        if redis_manager.is_available():
            update_session(session_id, {'is_recording': 'False'})
        else:
            session_data['is_recording'] = False
        
        # Get audio buffer
        if redis_manager.is_available():
            # Decode base64 string back to binary
            audio_buffer_b64 = session_data.get('audio_buffer', '')
            if not audio_buffer_b64:
                emit('transcription', {
                    'success': False,
                    'message': 'No audio data received.'
                })
                return
            audio_buffer = base64.b64decode(audio_buffer_b64)
        else:
            audio_buffer = session_data['audio_buffer']
        
        if len(audio_buffer) < 1000:  # Too short
            emit('transcription', {
                'success': False,
                'message': 'Audio too short. Please try again.'
            })
            return
        
        # Process audio asynchronously
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
                        return
                    # Convert Redis session data to expected format
                    session = {
                        'user_id': session_data.get('user_id'),
                        'user_name': session_data.get('user_name')
                    }
                else:
                    session = active_sessions.get(session_id)
                    if not session:
                        return
                
                print(f"🎧 Processing audio: {len(audio_buffer)} bytes")
                
                # Step 1: Transcribe audio using OpenAI Whisper
                socketio.emit('status', {'message': 'Transcribing...'}, namespace='/voice', room=session_id)
                
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
                    
                    # Send transcription to client
                    socketio.emit('transcription', {
                        'success': True,
                        'text': transcribed_text
                    }, namespace='/voice', room=session_id)
                    
                    # Step 2: Process with agent
                    socketio.emit('status', {'message': 'Processing request...'}, namespace='/voice', room=session_id)
                    
                    agent_response = asyncio.run(process_with_agent(
                        transcribed_text,
                        session['user_id'],
                        session['user_name']
                    ))
                    
                    print(f"🤖 Agent response: {agent_response}")
                    
                    # Step 3: Convert response to speech using OpenAI TTS
                    socketio.emit('status', {'message': 'Generating speech...'}, namespace='/voice', room=session_id)
                    
                    speech_response = openai_client.audio.speech.create(
                        model="tts-1",
                        voice="nova",  # Options: alloy, echo, fable, onyx, nova, shimmer
                        input=agent_response
                    )
                    
                    # Convert speech to base64 for transmission
                    audio_base64 = base64.b64encode(speech_response.content).decode('utf-8')
                    
                    # Send response to client
                    socketio.emit('agent_response', {
                        'success': True,
                        'text': agent_response,
                        'audio': audio_base64
                    }, namespace='/voice', room=session_id)
                
                finally:
                    # Clean up temp file
                    import os
                    if os.path.exists(temp_audio_path):
                        os.unlink(temp_audio_path)
            
            except Exception as e:
                print(f"❌ Error processing audio: {e}")
                import traceback
                traceback.print_exc()
                
                socketio.emit('error', {
                    'message': f"Error processing audio: {str(e)}"
                }, namespace='/voice', room=session_id)


async def process_with_agent(text: str, user_id: str, user_name: str) -> str:
    """Process user input with the agent"""
    try:
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
                return last_message.content
        
        return "I processed your request successfully."
    
    except asyncio.TimeoutError:
        return "I'm sorry, I'm taking too long to process that request. Please try again."
    except Exception as e:
        print(f"❌ Agent error: {e}")
        return "I'm sorry, I encountered an error. Please try again."

