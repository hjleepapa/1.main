# Convonet Voice Assistant - Interview Demo Script

## Pre-Demo Setup Checklist

- [ ] Test WebRTC connection in browser
- [ ] Test Twilio phone number for voice calls
- [ ] Verify Google Calendar integration
- [ ] Verify Todo integration
- [ ] Prepare test passcode (e.g., 1234)
- [ ] Have call center agent dashboard ready
- [ ] Prepare backup demo video if live demo fails

---

## Demo Script: Convonet Voice Assistant Platform

### Introduction (2 minutes)

**Opening Statement:**
"Thank you for the opportunity to demonstrate Convonet, a production-ready voice assistant platform I architected and built. This system integrates conversational AI with both web-based and telephony interfaces, using LLMs for natural language understanding and real-time voice interactions. Today I'll showcase its dual-channel architecture, conversation management, and seamless integration with external services."

**Key Points to Highlight:**
- Dual-channel support: WebRTC (browser) and Twilio (telephony)
- LLM-powered conversational AI with LangGraph
- Real-time voice interaction with ASR/TTS
- Tool integration (calendar, todos, CRM)
- Call center integration with agent handoff

---

### Part 1: WebRTC Voice Interface (3-4 minutes)

**Setup:**
1. Open browser to WebRTC voice assistant interface
2. Log in with test passcode (1234)

**Live Demo Flow:**

**Narrate:**
"First, I'll demonstrate the web-based voice interface using WebRTC for real-time audio communication."

**Actions:**
1. Click "Start Call" button
2. Grant microphone permissions
3. Wait for WebRTC connection establishment

**Key Talking Points:**
- "The system uses WebRTC for low-latency, peer-to-peer audio streaming, eliminating the need for traditional telephony infrastructure in browser environments."
- "Speech recognition is handled via Web Speech API, converting user audio to text in real-time."
- "We've implemented custom session management to maintain conversation context across multiple interactions."

**Test Interaction:**
- **User:** "Create a calendar event for a team meeting tomorrow at 2 PM"
- **Assistant:** [Responds, creates event via Google Calendar API]
- **Show:** Google Calendar opens with new event

**Narrate:**
"Notice how the assistant understands natural language intent, extracts structured data (date, time, event title), and executes actions through integrated APIs. This demonstrates our LLM integration with tool-calling capabilities."

---

### Part 2: Telephony Integration via Twilio (3-4 minutes)

**Setup:**
1. Dial the Twilio phone number from mobile phone
2. Enter passcode when prompted

**Live Demo Flow:**

**Narrate:**
"Now I'll demonstrate the same system through a traditional telephony interface using Twilio's Programmable Voice API."

**Actions:**
1. Call Twilio number from phone
2. Enter authentication passcode
3. Same conversation capabilities as WebRTC

**Test Interaction:**
- **User:** "Create a todo to follow up with the mortgage application"
- **Assistant:** [Responds, creates todo via integrated system]
- **Show:** Todo appears in dashboard

**Key Talking Points:**
- "The telephony integration uses Twilio's Voice API with TwiML for dynamic call control."
- "Same conversation engine powers both channels - ensuring consistent behavior across web and phone."
- "We've implemented DTMF support for authentication and fallback when speech recognition fails."
- "The system handles call quality degradation gracefully with fallback mechanisms."

---

### Part 3: Conversation Context & History (2 minutes)

**Narrate:**
"One critical requirement for voice bots is maintaining conversation context. Let me demonstrate our context management system."

**Actions:**
1. Make multiple interactions in sequence
2. Reference previous conversation
3. Show conversation history in UI

**Example Flow:**
- **User:** "Create a calendar event for interview next Monday at 10 AM"
- **Assistant:** [Creates event]
- **User:** "What did I just schedule?"
- **Assistant:** [References previous event creation]

**Key Talking Points:**
- "We use LangGraph's state management to maintain conversation thread context."
- "Each user session has a unique thread ID, allowing conversation history to persist across multiple calls."
- "The system tracks both user messages and tool execution results, enabling context-aware responses."
- "This is essential for handling multi-turn conversations and maintaining user intent across interactions."

---

### Part 4: Agent Handoff & Call Center Integration (3-4 minutes)

**Setup:**
1. From voice assistant, request transfer to human agent
2. Show call center dashboard receiving the call

**Live Demo Flow:**

**Narrate:**
"Enterprise voice bots need seamless escalation to human agents. I've built an integrated call center system with automatic context transfer."

**Actions:**
1. During voice call, say: "Transfer me to an agent" or "I need to speak with a human"
2. Call transfers to agent desktop (extension 2001)
3. Agent dashboard popup shows:
   - Customer information
   - Full conversation history
   - All activities performed (calendar events, todos)
   - Customer profile data

**Key Talking Points:**
- "The system uses intent detection to identify transfer requests."
- "Upon transfer, we cache the entire conversation context and customer profile in Redis."
- "The agent receives a popup with complete customer context, conversation history, and all actions taken during the voice assistant session."
- "This eliminates the 'can you repeat your issue' problem - agents have full context immediately."
- "The transfer mechanism supports both attended and blind transfers with SIP integration."

**Show Features:**
- Customer information popup with conversation history
- Activities section showing calendar events and todos
- Resizable, draggable popup window
- Call controls (answer, hold, transfer, hangup)

---

### Part 5: Technical Architecture Overview (3 minutes)

**Narrate:**
"Let me walk through the technical architecture that powers this system."

**Architecture Diagram Points:**

1. **Dual-Channel Input Layer:**
   - WebRTC Interface (Browser-based)
   - Twilio Telephony Interface (Phone-based)
   - Both feed into unified conversation engine

2. **Conversation Engine:**
   - LangGraph for state management and conversation orchestration
   - LLM integration (configured for multiple providers)
   - Tool-calling framework for API integrations
   - Intent detection and routing

3. **Tool Integration Layer:**
   - Google Calendar API (create events)
   - Todo/CRM system (task management)
   - Extensible MCP (Model Context Protocol) tool framework

4. **Session Management:**
   - Redis for caching customer profiles
   - Thread-based conversation persistence
   - Cross-session context sharing

5. **Call Center Integration:**
   - SIP/WebRTC agent desktop
   - Context transfer on escalation
   - Real-time call controls

**Key Talking Points:**
- "The architecture is modular - channels are pluggable, allowing easy addition of new interfaces."
- "We use a unified conversation engine, ensuring consistent behavior regardless of input channel."
- "The tool-calling framework uses MCP standards, making it easy to add new integrations."
- "Redis provides fast context caching for agent handoffs and session persistence."

---

### Part 6: Advanced Features (2 minutes)

**Topics to Cover:**

1. **Multi-Language Support:**
   - "The system is architected for multilingual support through MLM integration."
   - "The conversation engine can be configured to use different LLM models based on language detection."

2. **Fallback & Error Handling:**
   - "We've implemented graceful degradation - if speech recognition fails, we fall back to DTMF input."
   - "Tool execution errors are caught and handled with user-friendly error messages."
   - "Network issues trigger automatic reconnection logic."

3. **Scalability:**
   - "The system uses async/await patterns for non-blocking I/O."
   - "Redis caching reduces load on primary databases."
   - "Stateless API design allows horizontal scaling."

4. **Security & Compliance:**
   - "All voice data is processed in real-time and not permanently stored."
   - "Authentication required for both web and telephony access."
   - "Conversation data is encrypted in transit."

---

### Closing Statement (1 minute)

**Summary:**
"To summarize, Convonet demonstrates production-ready voice bot architecture with:
- Dual-channel support (web and telephony)
- LLM-powered conversational AI with context management
- Seamless agent handoff with full context transfer
- Extensible tool integration framework
- Enterprise-grade reliability and error handling

This system showcases the technical capabilities required for building intelligent voice interactions at scale, with a focus on user experience and operational efficiency."

**Transition to Q&A:**
"I'm happy to dive deeper into any aspect of the architecture or discuss how these patterns could be applied to AmeriSave's mortgage application workflows."

---

## Demo Tips

### Do's:
- ✅ Practice the demo flow multiple times
- ✅ Have backup screenshots/videos ready
- ✅ Test all integrations before demo day
- ✅ Prepare answers for common technical questions
- ✅ Show enthusiasm about voice AI technology
- ✅ Highlight problem-solving approach

### Don'ts:
- ❌ Don't apologize if something minor breaks
- ❌ Don't get lost in code details unless asked
- ❌ Don't rush through the demo
- ❌ Don't skip error handling scenarios
- ❌ Don't forget to highlight business value

---

## Backup Plan

If live demo fails:
1. Have pre-recorded video ready
2. Show architecture diagrams and code snippets
3. Walk through codebase structure
4. Discuss design decisions and trade-offs

---

## Potential Questions During Demo

**Be Ready For:**
- "How do you handle speech recognition errors?"
- "What's the latency between user speech and response?"
- "How do you scale this for thousands of concurrent users?"
- "How do you handle multilingual conversations?"
- "What's your approach to testing voice bots?"
- "How do you measure bot performance?"

