"""
WebRTC Voice Assistant Server
Provides high-quality audio streaming and real-time speech recognition
"""

import asyncio
import json
import os
import base64
from flask import Blueprint, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import openai
from sambanova.assistant_graph_todo import get_agent
from sambanova.state import AgentState
from langchain_core.messages import HumanMessage

webrtc_bp = Blueprint('webrtc_voice', __name__, url_prefix='/sambanova_todo/webrtc')

# Initialize OpenAI client for Whisper and TTS
openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Active sessions storage
active_sessions = {}

# Global references for background tasks
socketio = None
flask_app = None


@webrtc_bp.route('/voice-assistant')
def voice_assistant():
    """Render the WebRTC voice assistant interface"""
    return render_template('webrtc_voice_assistant.html')


def init_socketio(socketio_instance: SocketIO):
    """Initialize Socket.IO event handlers"""
    
    # Store socketio instance and Flask app for background tasks
    global socketio, flask_app
    socketio = socketio_instance
    
    # Get Flask app from current context (we're being called during app setup)
    from flask import current_app
    flask_app = current_app._get_current_object()
    
    @socketio.on('connect', namespace='/voice')
    def handle_connect():
        """Handle client connection"""
        session_id = request.sid
        print(f"✅ WebRTC client connected: {session_id}")
        
        # Initialize session
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
        
        if session_id in active_sessions:
            del active_sessions[session_id]
    
    
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
                    active_sessions[session_id]['authenticated'] = True
                    active_sessions[session_id]['user_id'] = str(user.id)
                    active_sessions[session_id]['user_name'] = user.first_name
                    
                    print(f"✅ Authentication successful: {user.email}")
                    
                    emit('authenticated', {
                        'success': True,
                        'user_name': user.first_name,
                        'message': f"Welcome back, {user.first_name}!"
                    })
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
        
        if session_id not in active_sessions:
            emit('error', {'message': 'Session not found'})
            return
        
        if not active_sessions[session_id]['authenticated']:
            emit('error', {'message': 'Please authenticate first'})
            return
        
        print(f"🎤 Recording started: {session_id}")
        active_sessions[session_id]['is_recording'] = True
        active_sessions[session_id]['audio_buffer'] = b''
        
        emit('recording_started', {'success': True})
    
    
    @socketio.on('audio_data', namespace='/voice')
    def handle_audio_data(data):
        """Receive audio data chunks from client"""
        session_id = request.sid
        
        if session_id not in active_sessions:
            return
        
        if not active_sessions[session_id]['is_recording']:
            return
        
        # Append audio chunk to buffer
        audio_chunk = base64.b64decode(data['audio'])
        active_sessions[session_id]['audio_buffer'] += audio_chunk
    
    
    @socketio.on('stop_recording', namespace='/voice')
    def handle_stop_recording():
        """Stop recording and process audio"""
        session_id = request.sid
        
        if session_id not in active_sessions:
            emit('error', {'message': 'Session not found'})
            return
        
        session = active_sessions[session_id]
        
        if not session['is_recording']:
            emit('error', {'message': 'Not recording'})
            return
        
        print(f"🛑 Recording stopped: {session_id}")
        session['is_recording'] = False
        
        # Get audio buffer
        audio_buffer = session['audio_buffer']
        
        if len(audio_buffer) < 1000:  # Too short
            emit('transcription', {
                'success': False,
                'message': 'Audio too short. Please try again.'
            })
            return
        
        # Process audio asynchronously
        socketio.start_background_task(process_audio_async, session_id, audio_buffer)
    
    
    def process_audio_async(session_id, audio_buffer):
        """Process audio in background task"""
        # Use the stored Flask app instance for application context
        with flask_app.app_context():
            try:
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
        # Get the agent
        agent = get_agent()
        graph = agent.build_graph()
        
        # Create initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=text)],
            customer_id="webrtc_user",
            authenticated_user_id=user_id,
            authenticated_user_name=user_name,
            is_authenticated=True
        )
        
        # Run agent with timeout
        result = await asyncio.wait_for(
            graph.ainvoke(initial_state),
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

