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

# Global agent graph cache (initialized on first use)
_agent_graph_cache = None
_agent_graph_lock = asyncio.Lock()

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
        
        # Verify PIN - use direct database query (fast, <100ms, avoids Twilio timeout)
        try:
            # Import here to avoid circular import
            from sambanova.mcps.local_servers.db_todo import _init_database, SessionLocal
            from sambanova.models.user_models import User as UserModel
            
            # Initialize database if needed
            _init_database()
            
            if SessionLocal is None:
                raise Exception("Database not initialized - DB_URI not configured")
            
            # Quick database lookup
            with SessionLocal() as session:
                user = session.query(UserModel).filter(
                    UserModel.voice_pin == clean_pin,
                    UserModel.is_active == True
                ).first()
            
            # Check if authentication succeeded
            if user:
                # Extract user info
                user_id = str(user.id)
                user_name = user.first_name
                
                # Store user ID in session (use call_sid as session key)
                # In production, use Redis or database for session storage
                
                response = VoiceResponse()
                gather = response.gather(
                    input='speech',
                    action=f'/sambanova_todo/twilio/process_audio?user_id={user_id}',
                    method='POST',
                    speech_timeout='auto',
                    timeout=10,
                    barge_in=True,
                    speech_model='experimental_conversations',  # Better conversational recognition
                    enhanced=True,  # Use enhanced speech recognition
                    language='en-US'  # Explicitly set language
                )
                
                # Welcome message
                gather.say(f"Welcome back, {user_name}! How can I help you today?", voice='Polly.Amy')
                
                response.say("I didn't hear anything. Please try again.", voice='Polly.Amy')
                response.redirect(f'/sambanova_todo/twilio/call?is_continuation=true&authenticated=true&user_id={user_id}')
                
                print(f"✅ PIN verified for user {user_id} ({user.email})")
                return Response(str(response), mimetype='text/xml')
            else:
                # Invalid PIN
                response = VoiceResponse()
                response.say("Invalid PIN. Please try again.", voice='Polly.Amy')
                response.redirect('/sambanova_todo/twilio/call')
                print(f"❌ Invalid PIN: {clean_pin}")
                return Response(str(response), mimetype='text/xml')
        
        except Exception as e:
            print(f"Error in database query: {e}")
            import traceback
            traceback.print_exc()
            response = VoiceResponse()
            response.say("There was an error verifying your PIN. Please try again.", voice='Polly.Amy')
            response.redirect('/sambanova_todo/twilio/call')
            return Response(str(response), mimetype='text/xml')
            
    except Exception as e:
        print(f"Error in verify_pin_webhook: {e}")
        import traceback
        traceback.print_exc()
        response = VoiceResponse()
        response.say("Sorry, there was a system error. Please try again.", voice='Polly.Amy')
        response.redirect('/sambanova_todo/twilio/call')
        return Response(str(response), mimetype='text/xml')

@sambanova_todo_bp.route('/twilio/transfer', methods=['POST'])
def transfer_to_agent():
    """
    Transfer the call to a FreePBX extension/queue.
    Expects POST parameters:
    - extension: The FreePBX extension or queue number to transfer to
    - call_sid: The Twilio Call SID
    """
    try:
        extension = request.form.get('extension') or request.args.get('extension', '201')
        call_sid = request.form.get('CallSid', '')
        
        logger.info(f"Transferring call {call_sid} to extension {extension}")
        
        # Create TwiML response for transfer
        response = VoiceResponse()
        response.say("Transferring you to an agent. Please wait.", voice='Polly.Amy')
        
        # Dial the FreePBX extension
        # Format: sip:extension@freepbx-domain
        freepbx_domain = os.getenv('FREEPBX_DOMAIN', '34.26.59.14')  # Use your FreePBX IP/domain
        sip_uri = f"sip:{extension}@{freepbx_domain}"
        
        response.dial(sip_uri)
        
        # If dial fails, provide fallback message
        response.say("I'm sorry, the transfer failed. Please try again later.", voice='Polly.Amy')
        response.hangup()
        
        logger.info(f"Transfer TwiML generated for call {call_sid} to {sip_uri}")
        return Response(str(response), mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"Error in transfer endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        response = VoiceResponse()
        response.say("I'm sorry, there was an error transferring your call. Please try again.", voice='Polly.Amy')
        response.hangup()
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
                barge_in=True,
                speech_model='experimental_conversations',  # Better conversational recognition
                enhanced=True,  # Use enhanced speech recognition
                language='en-US'  # Explicitly set language
            )
            gather.say("I didn't catch that. Could you please repeat?", voice='Polly.Amy')
            response.append(gather)
            
            # Fallback
            response.say("I didn't hear anything. Please try again.", voice='Polly.Amy')
            response.redirect(f'/sambanova_todo/twilio/call?is_continuation=true&authenticated=true{user_param}')
            return Response(str(response), mimetype='text/xml')
        
        # Check if user wants to transfer to an agent
        transfer_phrases = ['transfer', 'agent', 'human', 'representative', 'operator', 'speak to someone', 'talk to someone', 'real person']
        if any(phrase in transcribed_text.lower() for phrase in transfer_phrases):
            # Redirect to transfer endpoint
            webhook_base_url = get_webhook_base_url()
            response = VoiceResponse()
            response.redirect(f'{webhook_base_url}/sambanova_todo/twilio/transfer?extension=201')
            logger.info(f"Redirecting call to transfer endpoint based on user request: {transcribed_text}")
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
        
        # Check if agent response indicates a transfer request
        if agent_response.startswith("TRANSFER_INITIATED:"):
            # Parse transfer details
            transfer_data = agent_response.replace("TRANSFER_INITIATED:", "")
            parts = transfer_data.split("|")
            target_extension = parts[0] if len(parts) > 0 else "201"
            
            webhook_base_url = get_webhook_base_url()
            response = VoiceResponse()
            response.redirect(f'{webhook_base_url}/sambanova_todo/twilio/transfer?extension={target_extension}')
            logger.info(f"Agent initiated transfer to extension {target_extension}")
            return Response(str(response), mimetype='text/xml')
        
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
            barge_in=True,  # Enable barge-in to interrupt while speaking
            speech_model='experimental_conversations',  # Better conversational recognition
            enhanced=True,  # Use enhanced speech recognition
            language='en-US'  # Explicitly set language
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
    """Helper to initialize the agent graph with tools (cached for performance)."""
    global _agent_graph_cache
    
    # Return cached graph if available
    if _agent_graph_cache is not None:
        return _agent_graph_cache
    
    # Use lock to prevent multiple simultaneous initializations
    async with _agent_graph_lock:
        # Check again after acquiring lock (another thread might have initialized)
        if _agent_graph_cache is not None:
            return _agent_graph_cache
        
        print("🔧 Initializing agent graph (first time only)...")
        
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
            
            # Add call transfer tools (non-MCP tools)
            from .mcps.local_servers.call_transfer import get_transfer_tools
            transfer_tools = get_transfer_tools()
            tools.extend(transfer_tools)
            print(f"✅ Added {len(transfer_tools)} call transfer tools")
            
            print("🔧 Building agent graph...")
            
            # Build and cache the graph
            _agent_graph_cache = TodoAgent(tools=tools).build_graph()
            print("✅ Agent graph cached for future requests")
            
            return _agent_graph_cache
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
            tool_result = None
            async for state in stream:
                # Look for tool messages which contain the actual verification result
                if "messages" in state:
                    for msg in state["messages"]:
                        # Check if this is a ToolMessage with our authentication result
                        if hasattr(msg, 'content') and 'AUTHENTICATED:' in str(msg.content):
                            tool_result = msg.content
                            break
            
            # Return the tool result if found, otherwise authentication failed
            if tool_result:
                return tool_result
            return "AUTHENTICATION_FAILED: Invalid PIN"
        
        return await asyncio.wait_for(process_stream(), timeout=20.0)
    except asyncio.TimeoutError:
        print(f"PIN verification timeout for PIN: {pin}")
        return "AUTHENTICATION_FAILED: Verification timeout"
    except Exception as e:
        print(f"Error in PIN verification: {e}")
        import traceback
        traceback.print_exc()
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
