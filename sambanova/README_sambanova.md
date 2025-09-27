# Sambanova Todo Management System

A comprehensive productivity management system powered by Sambanova AI, featuring voice and web interfaces for task management, reminders, and calendar integration.

## Features

- **Natural Language Processing**: Powered by Sambanova AI for intelligent task understanding
- **Voice Interface**: Twilio integration for phone-based interactions
- **Web Interface**: Modern web-based todo management
- **Calendar Integration**: Automatic Google Calendar synchronization
- **Database Management**: PostgreSQL with dedicated sambanova tables
- **MCP Integration**: Model Context Protocol for tool integration
- **Call Recording**: Automatic recording and transcription of voice calls
- **WebSocket Support**: Real-time audio streaming for voice interactions

## Architecture

### Backend Components
- **Flask Application**: Web framework with blueprint-based routing
- **SQLAlchemy ORM**: Database abstraction layer
- **PostgreSQL**: Primary database with dedicated sambanova schema
- **MCP Server**: Database operations through Model Context Protocol

### AI Integration
- **Sambanova Models**: Core natural language processing
- **LangGraph**: State management for conversation flow
- **Tool Integration**: Database operations through MCP tools

### Voice Integration
- **Twilio**: Phone call handling and media streaming
- **Speech Recognition**: Automatic speech-to-text conversion
- **Voice Response**: Text-to-speech for user feedback

## Database Schema

### Tables
- `todos_sambanova`: Main todo items with priority and due dates
- `reminders_sambanova`: Reminder items with importance levels  
- `calendar_events_sambanova`: Calendar events synced with Google Calendar
- `call_recordings_sambanova`: Voice call recordings and transcriptions

### Key Fields
- **Todos**: id, title, description, completed, priority, due_date, google_calendar_event_id
- **Reminders**: id, reminder_text, importance, reminder_date, google_calendar_event_id
- **Calendar Events**: id, title, description, event_from, event_to, google_calendar_event_id
- **Call Recordings**: id, call_sid, recording_path, transcription, status

## API Endpoints

### Web Interface
- `GET /sambanova_todo/`: Main web interface
- `POST /sambanova_todo/run_agent`: Process natural language commands

### Voice Interface
- `POST /sambanova_todo/twilio/call`: Handle incoming voice calls
- `POST /sambanova_todo/twilio/process_audio`: Process voice input

## MCP Tools

The system provides the following MCP tools for database operations:

### Todo Management
- `create_todo`: Create new todo items
- `get_todos`: Retrieve all todos
- `complete_todo`: Mark todos as completed
- `update_todo`: Update todo properties
- `delete_todo`: Remove todos

### Reminder Management
- `create_reminder`: Create new reminders
- `get_reminders`: Retrieve all reminders
- `delete_reminder`: Remove reminders

### Calendar Management
- `create_calendar_event`: Create calendar events
- `get_calendar_events`: Retrieve all events
- `delete_calendar_event`: Remove calendar events

### Call Recording Management
- `create_call_recording`: Store call recordings
- `get_call_recordings`: Retrieve call history
- `update_call_recording`: Update recording metadata
- `delete_call_recording`: Remove recordings

### Database Operations
- `query_db`: Execute custom SQL queries

## Configuration

### Environment Variables
- `DB_URI`: PostgreSQL database connection string
- `FLASK_KEY`: Flask secret key for sessions
- `SAMBANOVA_API_KEY`: API key for Sambanova AI services
- `WEBHOOK_BASE_URL`: Base URL for Twilio webhooks (production)
- `WEBSOCKET_BASE_URL`: WebSocket URL for media streaming (production)

### MCP Configuration
Located in `mcps/mcp_config.json`, defines the database MCP server configuration.

## Usage

### Web Interface
1. Navigate to `/sambanova_todo/`
2. Use the web interface or API endpoints
3. Send JSON requests to `/sambanova_todo/run_agent`

### Voice Interface
1. Configure Twilio webhook to point to `/sambanova_todo/twilio/call`
2. Call the configured phone number
3. Speak naturally to create and manage todos

### API Usage
```bash
curl -X POST /sambanova_todo/run_agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a todo to buy groceries"}'
```

## Development

### Local Development
1. Set up PostgreSQL database
2. Configure environment variables (hjlees.com URLs are pre-configured)
3. Run Flask application

### Production Deployment
1. Set production environment variables (hjlees.com URLs are pre-configured)
2. Deploy Flask application to hjlees.com webserver
3. SSL certificates are handled by the hjlees.com webserver

## Integration

### Google Calendar
- Automatic event creation for todos and reminders
- Bidirectional synchronization
- Event updates and deletions

### Twilio
- Voice call handling
- Speech recognition
- Media streaming support
- Call recording capabilities

### Sambanova AI
- Natural language understanding
- Context-aware responses
- Intelligent task categorization
- Priority assignment

## File Structure

```
sambanova/
├── __init__.py                 # Blueprint registration
├── routes.py                   # Flask routes and webhooks
├── models.py                   # Database models
├── state.py                    # LangGraph state management
├── assistant_graph_todo.py     # Sambanova AI agent configuration
├── twilio_handler.py           # Twilio WebSocket handler for voice calls
├── http_websocket_server.py    # Hybrid HTTP/WebSocket server
├── voice_utils.py              # Voice processing utilities
├── generate_tables.sql         # Database table creation script
├── templates/                  # HTML templates
│   └── sambanova_todo_index.html
├── static/                     # Static assets
│   └── assets/
│       ├── css/
│       ├── js/
│       └── img/
├── mcps/                       # MCP configuration
│   ├── mcp_config.json
│   └── local_servers/
│       └── db_todo.py          # Database MCP server
└── README_sambanova.md         # This file
```

## Dependencies

- Flask
- SQLAlchemy
- PostgreSQL
- LangGraph
- LangChain
- Sambanova AI
- Twilio
- MCP (Model Context Protocol)
- Google Calendar API

## License

This project is part of the main Flask application and follows the same licensing terms.
