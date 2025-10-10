from flask import Blueprint, request, jsonify, render_template, Response
from flask_socketio import emit, join_room, leave_room
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
from typing import Optional
import asyncio
import json
import os
import logging

from twilio.twiml.voice_response import VoiceResponse, Connect, Gather
from .state import AgentState
from .assistant_graph_todo import get_agent, TodoAgent
from langchain_mcp_adapters.client import MultiServerMCPClient

# Import new authentication and team routes
from .api_routes.auth_routes import auth_bp
from .api_routes.team_routes import team_bp
from .api_routes.team_todo_routes import team_todo_bp

# Set up logging
logger = logging.getLogger(__name__)


sambanova_todo_bp = Blueprint(
    'sambanova_todo',
    __name__,
    url_prefix='/sambanova_todo',
    template_folder='templates',
    static_folder='static'
)

def get_webhook_base_url():
    """Get the webhook base URL for Twilio webhooks."""
    # Use hjlees.com webserver for all environments
    return os.getenv('WEBHOOK_BASE_URL', 'https://hjlees.com')

def get_websocket_url():
    """Get the WebSocket URL for Twilio Media Streams."""
    # Use integrated WebSocket endpoint on hjlees.com
    return os.getenv('WEBSOCKET_BASE_URL', 'wss://hjlees.com/sambanova_todo/ws')

# --- Twilio Voice Routes ---
@sambanova_todo_bp.route('/twilio/call', methods=['POST'])
def twilio_call_webhook():
    """
    Handles incoming calls from Twilio.
    Asks for PIN authentication before allowing access to the assistant.
    """
    # Get the current webhook base URL
    webhook_base_url = get_webhook_base_url()
    
    # Check if this is a continuation of the conversation
    is_continuation = request.args.get('is_continuation', 'false').lower() == 'true'
    # Check if user is already authenticated in this session
    is_authenticated = request.args.get('authenticated', 'false').lower() == 'true'
    
    response = VoiceResponse()
    
    # If not authenticated, ask for PIN
    if not is_authenticated and not is_continuation:
        gather = response.gather(
            input='dtmf speech',  # Accept both DTMF (keypad) and speech
            action='/sambanova_todo/twilio/verify_pin',
            method='POST',
            timeout=10,
            finish_on_key='#'  # Press # to finish (for DTMF), no num_digits requirement
        )
        gather.say("Welcome to Sambanova productivity assistant. Please enter or say your 4 to 6 digit PIN, then press pound.", voice='Polly.Amy')
        
        response.say("I didn't receive a PIN. Please try again.", voice='Polly.Amy')
        response.redirect('/sambanova_todo/twilio/call')
        
        print(f"Generated TwiML for PIN request: {str(response)}")
        return Response(str(response), mimetype='text/xml')
    
    # User is authenticated, proceed with normal conversation
    gather = response.gather(
        input='speech',
        action='/sambanova_todo/twilio/process_audio',
        method='POST',
        speech_timeout='auto',
        timeout=10,
        barge_in=True
    )
    
    # Only say the welcome message if this is the first authenticated interaction
    if not is_continuation:
        gather.say("How can I help you today?", voice='Polly.Amy')
    
    # Fallback if no speech is detected
    response.say("I didn't hear anything. Please try again.", voice='Polly.Amy')
    response.redirect('/sambanova_todo/twilio/call?is_continuation=true&authenticated=true')
    
    print(f"Generated TwiML for incoming call: {str(response)}")
    return Response(str(response), mimetype='text/xml')

@sambanova_todo_bp.route('/twilio/verify_pin', methods=['POST'])
def verify_pin_webhook():
    """
    Verifies the user's PIN and authenticates the session.
    """
    try:
        # Get PIN from either DTMF digits or speech
        pin = request.form.get('Digits', '') or request.form.get('SpeechResult', '')
        call_sid = request.form.get('CallSid', '')
        
        print(f"Verifying PIN for call {call_sid}: {pin}")
        
        if not pin:
            response = VoiceResponse()
            response.say("I didn't receive a PIN. Please try again.", voice='Polly.Amy')
            response.redirect('/sambanova_todo/twilio/call')
            return Response(str(response), mimetype='text/xml')
        
        # Convert spoken numbers to digits
        number_words = {
            'zero': '0', 'oh': '0', 'o': '0',
            'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
            'ten': '10', 'eleven': '11', 'twelve': '12'
        }
        
        # Clean up the PIN - remove non-alphanumeric except spaces
        # This handles cases like "1234." from DTMF or "one two three four" from speech
        cleaned_input = pin.strip()
        
        # First, try to extract any digits directly (handles DTMF like "1234" or "1234.")
        digits_only = ''.join(c for c in cleaned_input if c.isdigit())
        
        # If we got digits directly (DTMF input), use them
        if digits_only and len(digits_only) >= 4:
            clean_pin = digits_only
        else:
            # No direct digits, try speech-to-digit conversion
            words = cleaned_input.lower().replace('-', ' ').replace(',', ' ').replace('.', ' ').split()
            converted_digits = []
            for word in words:
                if word in number_words:
                    converted_digits.append(number_words[word])
                elif word.isdigit():
                    converted_digits.append(word)
            clean_pin = ''.join(converted_digits)
        
        print(f"🔧 Original PIN: '{pin}' → Cleaned PIN: '{clean_pin}'")
        
        if not clean_pin or len(clean_pin) < 4 or len(clean_pin) > 6:
            response = VoiceResponse()
            response.say("Invalid PIN format. Please enter a 4 to 6 digit PIN.", voice='Polly.Amy')
            response.redirect('/sambanova_todo/twilio/call')
            return Response(str(response), mimetype='text/xml')
        
        # Verify PIN using MCP tool
        try:
            verification_result = asyncio.run(_run_agent_for_pin_verification(clean_pin))
            
            # Check if authentication succeeded
            if "AUTHENTICATED:" in verification_result:
                # Extract user ID from result
                parts = verification_result.split('\n\n')[0].split('|')
                user_id = parts[0].replace('AUTHENTICATED:', '')
                user_name = parts[1] if len(parts) > 1 else "User"
                
                # Store user ID in session (use call_sid as session key)
                # In production, use Redis or database for session storage
                
                response = VoiceResponse()
                gather = response.gather(
                    input='speech',
                    action=f'/sambanova_todo/twilio/process_audio?user_id={user_id}',
                    method='POST',
                    speech_timeout='auto',
                    timeout=10,
                    barge_in=True
                )
                
                # Extract welcome message from verification result
                welcome_msg = verification_result.split('\n\n', 1)[1] if '\n\n' in verification_result else f"Welcome, {user_name}!"
                gather.say(f"{welcome_msg} How can I help you today?", voice='Polly.Amy')
                
                response.say("I didn't hear anything. Please try again.", voice='Polly.Amy')
                response.redirect(f'/sambanova_todo/twilio/call?is_continuation=true&authenticated=true&user_id={user_id}')
                
                print(f"✅ PIN verified for user {user_id}")
                return Response(str(response), mimetype='text/xml')
            else:
                # Authentication failed
                response = VoiceResponse()
                response.say("Invalid PIN. Please try again.", voice='Polly.Amy')
                response.redirect('/sambanova_todo/twilio/call')
                print(f"❌ PIN verification failed")
                return Response(str(response), mimetype='text/xml')
                
        except asyncio.TimeoutError:
            response = VoiceResponse()
            response.say("Authentication timed out. Please try again.", voice='Polly.Amy')
            response.redirect('/sambanova_todo/twilio/call')
            return Response(str(response), mimetype='text/xml')
            
    except Exception as e:
        print(f"Error in PIN verification: {e}")
        response = VoiceResponse()
        response.say("There was an error verifying your PIN. Please try again.", voice='Polly.Amy')
        response.redirect('/sambanova_todo/twilio/call')
        return Response(str(response), mimetype='text/xml')

@sambanova_todo_bp.route('/twilio/process_audio', methods=['POST'])
def process_audio_webhook():
    """
    Handles audio processing requests from Twilio.
    Processes the audio and returns TwiML with the agent's response.
    
    Features:
    - Barge-in capability: Users can interrupt the agent while it's speaking
    - Continuous conversation flow
    - Graceful error handling
    """
    try:
        # Get the transcribed text from the request
        transcribed_text = request.form.get('SpeechResult', '')
        call_sid = request.form.get('CallSid', '')
        
        print(f"Processing audio for call {call_sid}: {transcribed_text}")
        
        if not transcribed_text or len(transcribed_text.strip()) < 2:
            response = VoiceResponse()
            
            # Get authenticated user_id for redirect
            user_id = request.args.get('user_id', '')
            user_param = f'&user_id={user_id}' if user_id else ''
            
            # Use Gather with barge-in for "didn't catch that" response
            gather = Gather(
                input='speech',
                action=f'/sambanova_todo/twilio/process_audio?user_id={user_id}' if user_id else '/sambanova_todo/twilio/process_audio',
                method='POST',
                speech_timeout='auto',
                timeout=10,
                barge_in=True
            )
            gather.say("I didn't catch that. Could you please repeat?", voice='Polly.Amy')
            response.append(gather)
            
            # Fallback
            response.say("I didn't hear anything. Please try again.", voice='Polly.Amy')
            response.redirect(f'/sambanova_todo/twilio/call?is_continuation=true&authenticated=true{user_param}')
            return Response(str(response), mimetype='text/xml')
        
        # Check if user wants to end the call
        exit_phrases = ['exit', 'goodbye', 'bye', 'that\'s it', 'that is it', 'thank you', 'thanks', 'done', 'finished', 'end call', 'hang up']
        if any(phrase in transcribed_text.lower() for phrase in exit_phrases):
            # End the call gracefully
            response = VoiceResponse()
            response.say("Thank you for using Sambanova productivity assistant! Have a great day!", voice='Polly.Amy')
            response.hangup()
            return Response(str(response), mimetype='text/xml')
        
        # Get authenticated user_id from query params
        user_id = request.args.get('user_id')
        
        # Process with the agent (with timeout to prevent hanging)
        try:
            agent_response = asyncio.run(asyncio.wait_for(
                _run_agent_async(transcribed_text, user_id=user_id),
                timeout=30.0
            ))
        except asyncio.TimeoutError:
            agent_response = "I'm sorry, I'm taking too long to process that request. Please try again with a simpler request."
        except Exception as e:
            print(f"Error in agent processing: {e}")
            agent_response = "I'm sorry, I encountered an error processing your request. Please try again."
        
        # Return TwiML with the agent's response and barge-in capability
        response = VoiceResponse()
        
        # Preserve user_id in redirects
        user_param = f'?user_id={user_id}' if user_id else ''
        auth_param = f'&authenticated=true' if user_id else ''
        
        # Use Gather with speech input to enable barge-in functionality
        gather = Gather(
            input='speech',
            action=f'/sambanova_todo/twilio/process_audio{user_param}',
            method='POST',
            speech_timeout='auto',
            timeout=10,
            barge_in=True  # Enable barge-in to interrupt while speaking
        )
        
        # Add the agent's response to the gather
        gather.say(agent_response, voice='Polly.Amy')
        response.append(gather)
        
        # Fallback if no speech is detected after the response
        response.say("I didn't hear anything. Please try again.", voice='Polly.Amy')
        response.redirect(f'/sambanova_todo/twilio/call?is_continuation=true{auth_param}{user_param}')
        
        print(f"Generated TwiML response: {str(response)}")
        return Response(str(response), mimetype='text/xml')
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        response = VoiceResponse()
        
        # Preserve user_id in error redirects
        user_id = request.args.get('user_id', '')
        user_param = f'?user_id={user_id}' if user_id else ''
        auth_param = f'&authenticated=true' if user_id else ''
        
        # Use Gather with barge-in for error messages too
        gather = Gather(
            input='speech',
            action=f'/sambanova_todo/twilio/process_audio{user_param}',
            method='POST',
            speech_timeout='auto',
            timeout=10,
            barge_in=True
        )
        gather.say("I'm sorry, I encountered an error processing your request. Please try again.", voice='Polly.Amy')
        response.append(gather)
        
        # Fallback
        response.say("I didn't hear anything. Please try again.", voice='Polly.Amy')
        response.redirect(f'/sambanova_todo/twilio/call?is_continuation=true{auth_param}{user_param}')
        return Response(str(response), mimetype='text/xml')

# WebSocket server is now handled by a separate process
# See websocket_server.py for the Twilio voice streaming implementation

# --- Web/API Routes ---
@sambanova_todo_bp.route('/')
def index():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'sambanova_todo_index.html')
    if os.path.exists(template_path):
        return render_template('sambanova_todo_index.html')
    return "Sambanova Todo: Sambanova + MCP integration is ready. POST to /sambanova_todo/run_agent with JSON {prompt: str}."


async def _get_agent_graph() -> StateGraph:
    """Helper to initialize the agent graph with tools."""
    config_path = os.path.join(os.path.dirname(__file__), 'mcps', 'mcp_config.json')
    if not os.path.exists(config_path):
        # Fallback path for when running from the root directory
        config_path = os.path.join('sambanova', 'mcps', 'mcp_config.json')

    with open(config_path) as f:
        mcp_config = json.load(f)
    
    # Set working directory to project root for MCP servers
    # __file__ is: /Users/hj/Web Development Projects/1. Main/sambanova/routes.py
    # We need: /Users/hj/Web Development Projects/1. Main
    project_root = os.path.dirname(os.path.dirname(__file__))
    original_cwd = os.getcwd()
    os.chdir(project_root)
    
    # Update the MCP config with absolute paths and environment variables
    for server_name, server_config in mcp_config["mcpServers"].items():
        if "args" in server_config and len(server_config["args"]) > 0:
            # Convert relative path to absolute path
            relative_path = server_config["args"][0]
            if not os.path.isabs(relative_path):
                absolute_path = os.path.join(project_root, relative_path)
                server_config["args"][0] = absolute_path
        
        # Handle environment variable substitution in env section
        if "env" in server_config:
            for env_key, env_value in server_config["env"].items():
                if isinstance(env_value, str) and env_value.startswith("${") and env_value.endswith("}"):
                    # Extract environment variable name
                    env_var_name = env_value[2:-1]
                    env_var_value = os.getenv(env_var_name)
                    if env_var_value:
                        server_config["env"][env_key] = env_var_value
                        print(f"🔧 MCP config: Set {env_key}={env_var_name} from environment")
                    else:
                        print(f"⚠️  MCP config: Environment variable {env_var_name} not found")
    
    try:
        # Initialize MCP client (langchain-mcp-adapters 0.1.0+ does not support context manager)
        print("🔧 Creating MCP client...")
        client = MultiServerMCPClient(connections=mcp_config["mcpServers"])
        print("🔧 Getting tools from MCP client...")
        tools = await asyncio.wait_for(client.get_tools(), timeout=10.0)
        print(f"✅ MCP client initialized successfully with {len(tools)} tools")
        print("🔧 Building agent graph...")
        return TodoAgent(tools=tools).build_graph()
    except asyncio.TimeoutError:
        print("❌ MCP client initialization timed out after 10 seconds")
        raise Exception("Database connection timed out. Please try again.")
    except Exception as e:
        print(f"❌ Error initializing MCP client: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise Exception(f"Database initialization failed: {str(e)}")
    finally:
        os.chdir(original_cwd)


async def _run_agent_for_pin_verification(pin: str) -> str:
    """Run agent specifically for PIN verification."""
    try:
        agent_graph = await _get_agent_graph()
        
        # Create a state that will trigger verify_user_pin tool
        input_state = AgentState(
            messages=[HumanMessage(content=f"User is authenticating with PIN: {pin}. Please verify their PIN using the verify_user_pin tool.")],
            customer_id="",
            is_authenticated=False
        )
        config = {"configurable": {"thread_id": f"pin-verify-{pin}"}}
        
        # Stream through the graph
        stream = agent_graph.astream(input=input_state, stream_mode="values", config=config)
        
        async def process_stream():
            async for _ in stream:
                pass
            final_state = agent_graph.get_state(config=config)
            last_message = final_state.values.get("messages")[-1]
            return getattr(last_message, 'content', "")
        
        return await asyncio.wait_for(process_stream(), timeout=10.0)
    except Exception as e:
        print(f"Error in PIN verification: {e}")
        return f"AUTHENTICATION_ERROR: {str(e)}"

async def _run_agent_async(prompt: str, user_id: Optional[str] = None, user_name: Optional[str] = None) -> str:
    """Runs the agent for a given prompt and returns the final response."""
    try:
        agent_graph = await _get_agent_graph()
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return "I'm sorry, there's a temporary system issue. Please try again in a moment."

    input_state = AgentState(
        messages=[HumanMessage(content=prompt)],
        customer_id="",
        authenticated_user_id=user_id,
        authenticated_user_name=user_name,
        is_authenticated=bool(user_id)
    )
    config = {"configurable": {"thread_id": f"user-{user_id}" if user_id else "flask-thread-1"}}

    # Stream through the graph to execute the agent logic with timeout
    try:
        # Create the async iterator first
        stream = agent_graph.astream(input=input_state, stream_mode="values", config=config)
        
        # Use wait_for to wrap the entire async for loop
        async def process_stream():
            async for _ in stream:
                pass
            final_state = agent_graph.get_state(config=config)
            last_message = final_state.values.get("messages")[-1]
            return getattr(last_message, 'content', "")
        
        return await asyncio.wait_for(process_stream(), timeout=25.0)
    except asyncio.TimeoutError:
        return "I'm sorry, I'm taking too long to process that request. Please try again with a simpler request."
    except Exception as e:
        print(f"Error in agent execution: {e}")
        return "I'm sorry, I encountered an error processing your request. Please try again."


@sambanova_todo_bp.route('/run_agent', methods=['POST'])
def run_agent():
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "Missing 'prompt' in JSON body"}), 400

    try:
        result = asyncio.run(_run_agent_async(prompt))
        return jsonify({"result": result})
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in /run_agent: {e}")
        return jsonify({"error": str(e)}), 500


# WebSocket event handlers for Flask-SocketIO
@sambanova_todo_bp.route('/ws')
def websocket_route():
    """WebSocket route for Twilio Media Streams."""
    return "WebSocket endpoint available via Socket.IO", 200


def register_socketio_events(socketio):
    """Register Socket.IO events for Sambanova WebSocket functionality."""
    
    @socketio.on('connect', namespace='/sambanova_todo')
    def handle_connect():
        """Handle WebSocket connection from Twilio."""
        logger.info(f"WebSocket connection established from {request.remote_addr}")
        emit('status', {'msg': 'Connected to Sambanova WebSocket'})
    
    @socketio.on('disconnect', namespace='/sambanova_todo')
    def handle_disconnect():
        """Handle WebSocket disconnection."""
        logger.info(f"WebSocket connection closed from {request.remote_addr}")
    
    @socketio.on('media', namespace='/sambanova_todo')
    def handle_media(data):
        """Handle media data from Twilio."""
        try:
            # Process media data from Twilio Media Streams
            logger.info(f"Received media data: {len(data)} bytes")
            
            # Here you would integrate with the twilio_handler logic
            # For now, just acknowledge receipt
            emit('ack', {'msg': 'Media received'})
            
        except Exception as e:
            logger.error(f"Error handling media: {str(e)}", exc_info=True)
            emit('error', {'msg': str(e)})
    
    @socketio.on('start', namespace='/sambanova_todo')
    def handle_start(data):
        """Handle start event from Twilio."""
        try:
            logger.info(f"Start event received: {data}")
            
            # Initialize conversation with Sambanova agent
            emit('started', {'msg': 'Conversation started with Sambanova agent'})
            
        except Exception as e:
            logger.error(f"Error handling start: {str(e)}", exc_info=True)
            emit('error', {'msg': str(e)})
    
    @socketio.on('stop', namespace='/sambanova_todo')
    def handle_stop(data):
        """Handle stop event from Twilio."""
        try:
            logger.info(f"Stop event received: {data}")
            
            # Clean up conversation
            emit('stopped', {'msg': 'Conversation ended'})
            
        except Exception as e:
            logger.error(f"Error handling stop: {str(e)}", exc_info=True)
            emit('error', {'msg': str(e)})
