# ConvoNet - AI-Powered Voice Assistant for Productivity & Call Center Operations

## Inspiration

ConvoNet was born from the frustration of juggling multiple productivity tools—task management, calendar scheduling, team collaboration, and customer service—all while maintaining context across voice and text interfaces. We envisioned a unified AI assistant that could seamlessly handle everything from creating team todos during a phone call to intelligently routing customer inquiries to the right agent, all while maintaining a natural conversational flow.

The inspiration came from watching customer service teams struggle with context switching between CRMs, ticketing systems, and communication platforms. We wanted to build something that understands natural language intent, remembers context across sessions, and automates the tedious parts of productivity and customer service workflows.

## What it does

ConvoNet is an AI-powered voice and text assistant that integrates productivity management with intelligent call center operations. It provides:

**Voice Assistant Features:**
- **PIN-authenticated voice access** via Twilio Programmable Voice
- **Natural language task management**: "Create a reminder to follow up with John tomorrow at 2 PM" - creates both a todo and calendar event
- **Team collaboration**: Access and manage team todos and calendar events through voice commands
- **Intelligent call transfers**: Seamlessly transfer calls to human agents with full context and customer profile popups

**Call Center Dashboard:**
- **SIP-based agent interface** using JsSIP for browser-based phone calls
- **Real-time customer information popups** showing caller history, account status, and open tickets
- **Automatic customer profile caching** from Redis for instant agent context
- **Call transfer capabilities** (blind and attended) with SIP REFER support

**Backend Integrations:**
- **LangGraph-powered agent orchestration** for complex multi-step workflows
- **PostgreSQL database** for todos, calendar events, teams, and user management
- **Redis caching** for session management and real-time customer profiles
- **Google Calendar API** integration for event creation and synchronization
- **Twilio integration** for voice calls and call center operations
- **FreeSWITCH SIP server** for call routing and bridging

**Security & Authentication:**
- **JWT-based authentication** with refresh tokens
- **Team-based access control** with role-based permissions (owner, admin, member, viewer)
- **Frontegg FrontMCP integration** (partial) - attempted enterprise-grade auth-as-a-service for multi-tenant SSO

## How we built it

**Tech Stack:**
- **Backend**: Flask (Python) with Flask-SocketIO for WebSocket support
- **AI Framework**: LangGraph for conversational state management, LangChain for tool orchestration
- **Voice Processing**: Twilio Programmable Voice, Deepgram SDK for real-time transcription
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis for sessions and customer profiles
- **Frontend**: Vanilla JavaScript with JsSIP library for SIP WebRTC calls
- **Voice UI**: TwiML for IVR flows and call routing
- **MCP Integration**: Model Context Protocol adapters for tool standardization

**Architecture:**
1. **Voice Flow**: User calls Twilio number → PIN authentication → WebRTC audio stream → Deepgram transcription → LangGraph agent processes → OpenAI TTS response
2. **Agent Dashboard**: Browser-based SIP client connects to FreeSWITCH → Receives calls from Twilio bridges → Displays customer info from Redis cache
3. **API Layer**: RESTful endpoints protected with JWT auth decorators → Team-based permission checks → Database/Redis operations
4. **Agent Tools**: LangGraph tools for todo/calendar operations → MCP adapters for standardized tool calls → Direct database operations with session management

**Key Components:**
- `webrtc_voice_server.py`: WebSocket server handling real-time audio streaming and transcription
- `assistant_graph_todo.py`: LangGraph state machine for conversational agent
- `call_center/`: Full-featured agent dashboard with SIP integration
- `api_routes/`: Team management, todos, calendar, and authentication endpoints
- `mcps/local_servers/`: MCP tools for database, calendar, and call transfer operations
- `security/auth.py`: JWT authentication with optional Frontegg token validation

**Integration Attempts:**
- **Frontegg FrontMCP**: Attempted to integrate enterprise auth-as-a-service for multi-tenant SSO support, but deployment encountered issues
- **FrontMCP Server**: Created TypeScript-based MCP server (`frontmcp/`) following official FrontMCP documentation to expose ConvoNet tools via MCP protocol

## Challenges we ran into

**1. SIP Call Handling & Duplicate INVITEs**
- FreeSWITCH was forking multiple SIP INVITE legs when bridging calls from Twilio to agent extensions
- **Solution**: Implemented session tracking in the browser (JsSIP) to ignore duplicate parallel sessions instead of rejecting them, preventing "agent busy" false positives

**2. Customer Profile Display**
- Agent dashboard was showing incorrect customer information (default mock data) instead of authenticated user data
- **Solution**: Enhanced Redis caching to store complete customer profiles from authenticated sessions and modified the customer lookup API to prioritize cached data over fallback mocks

**3. Voice PIN Authentication Timing**
- Twilio webhook timeout (<10s) required fast PIN validation
- **Solution**: Direct database queries with indexed `voice_pin` column, avoiding ORM overhead and ensuring sub-100ms response times

**4. Database Initialization in MCP Tools**
- Agent tools were failing with "'NoneType' object is not callable" errors
- **Solution**: Added explicit `check_database_available()` calls before opening SQLAlchemy sessions in MCP tool handlers

**5. Frontegg FrontMCP Deployment Failure**
- Attempted to integrate Frontegg's auth-as-a-service for enterprise SSO capabilities
- **Challenges**: 
  - Complex OAuth configuration with multiple redirect URLs
  - Client secret generation required enabling server-to-server access, which wasn't immediately clear in the UI
  - FrontMCP server deployment encountered environment variable mismatches and token validation edge cases
- **Status**: Partial integration - backend code supports Frontegg token validation, but full deployment and frontend integration incomplete due to time constraints

**6. Render.com Build Process**
- Initially, gunicorn wasn't found during deployment because the start command wasn't using the Python virtual environment
- **Solution**: Updated `render.yaml` to use `python -m gunicorn` instead of direct `gunicorn` command and created a build script that handles both Python and Node.js dependencies

**7. WebRTC Audio Stream Latency**
- Real-time transcription needed to handle audio chunks efficiently without blocking
- **Solution**: Async WebSocket handlers with eventlet for concurrent audio processing and proper buffering

## Accomplishments that we're proud of

1. **Unified Voice & Text Interface**: Successfully built a single AI assistant that handles both voice calls and API requests with consistent behavior and context preservation

2. **End-to-End Call Center Integration**: Complete SIP-to-Twilio bridging with customer profile popups, showing real-time data from authenticated sessions

3. **Robust Team Collaboration**: Full CRUD operations for team todos and calendar events with role-based permissions, all accessible through natural language voice commands

4. **Production-Ready Architecture**: Scalable Redis caching, PostgreSQL persistence, WebSocket real-time communication, and proper JWT authentication with refresh tokens

5. **MCP Protocol Compliance**: Successfully created MCP tools for database and calendar operations, making ConvoNet's capabilities accessible through the Model Context Protocol standard

6. **Performance Optimization**: Sub-100ms PIN authentication, efficient Redis caching for customer profiles, and optimized database queries for real-time call center operations

7. **Error Handling & Resilience**: Comprehensive error handling in voice flows, graceful fallbacks for missing customer data, and session management that survives network interruptions

8. **Developer Experience**: Clean separation of concerns, well-documented API routes, and modular MCP tool structure that makes extending functionality straightforward

## What we learned

**Technical Learnings:**
- **SIP Protocol Nuances**: FreeSWITCH call forking can create multiple INVITE legs; handling these gracefully requires understanding SIP state machines and not rejecting parallel sessions
- **WebRTC Audio Streaming**: Deepgram's real-time transcription requires careful buffer management and async processing to avoid audio dropouts
- **LangGraph State Management**: Using state machines for conversational AI provides better control over multi-step workflows than purely stateless chat completions
- **Redis as Session Store**: Using Redis for temporary customer profiles enables fast lookups while preventing stale data through TTL management

**Integration Challenges:**
- **Third-Party Auth Providers**: Enterprise SSO solutions like Frontegg require careful OAuth configuration, especially when enabling server-to-server access; UI workflows aren't always intuitive
- **MCP Protocol**: The Model Context Protocol standardizes tool interfaces well, but integrating with existing LangGraph agents required adapter layers
- **Deployment Complexity**: Multi-language projects (Python + TypeScript) require careful build process orchestration on platforms like Render.com

**Product Insights:**
- **Voice UX**: Users expect immediate feedback; even sub-second delays in PIN validation feel slow during phone calls
- **Context Preservation**: Maintaining customer context across voice calls, agent transfers, and API requests requires careful session management
- **Agent Efficiency**: Populating customer information automatically (from Redis cache) dramatically reduces agent lookup time during live calls

## What's next for ConvoNet

**Short-term (Next Sprint):**
1. **Complete Frontegg Integration**: Resolve deployment issues, enable full multi-tenant SSO, and integrate FrontMCP server with production authentication
2. **Enhanced Voice Features**: Add support for multi-language recognition, voice command shortcuts, and personalized greetings based on user history
3. **Call Analytics**: Implement call recording analysis, sentiment tracking, and automatic ticket creation from call transcripts

**Medium-term (Next Quarter):**
1. **AI Agent Improvements**: 
   - Fine-tune intent recognition for better task/calendar parsing
   - Add multi-turn conversation memory across sessions
   - Implement proactive reminders and follow-up suggestions
2. **Advanced Call Center Features**:
   - Predictive customer routing based on agent expertise
   - Real-time supervisor dashboards with call monitoring
   - Integration with CRM systems (Salesforce, HubSpot)
3. **Team Collaboration Enhancements**:
   - Real-time collaborative todo editing
   - Team activity feeds and notifications
   - Advanced permission models with custom roles

**Long-term Vision:**
1. **Multi-Channel Support**: Extend beyond voice to SMS, email, and chat platforms (Slack, Microsoft Teams)
2. **Custom Agent Training**: Allow teams to train ConvoNet on their specific workflows and terminology
3. **Enterprise Features**: Multi-workspace support, advanced analytics dashboards, compliance logging (HIPAA, SOC 2)
4. **Open Source MCP Tools**: Release ConvoNet's MCP tools as a standalone package for the community
5. **API Marketplace**: Enable third-party developers to build integrations using ConvoNet's agent capabilities

**Technical Debt & Improvements:**
- Migrate from eventlet to async/await patterns for better Python 3.12+ compatibility
- Add comprehensive integration tests for voice flows and SIP call handling
- Implement rate limiting on API endpoints to prevent abuse
- Add monitoring and alerting (Sentry integration partially complete)
- Optimize database queries with proper indexing and connection pooling

---

**Built with ❤️ for the Hackathon**

*ConvoNet: Where voice meets productivity, and AI understands your workflow.*

