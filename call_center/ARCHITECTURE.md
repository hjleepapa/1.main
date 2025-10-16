# Call Center Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Call Center System                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Browser    │────▶│  Flask API   │────▶│  PostgreSQL  │
│  (Agent UI)  │◀────│   (Backend)  │◀────│  (Database)  │
└──────────────┘     └──────────────┘     └──────────────┘
       │                     │
       │ WSS                 │
       │                     │
       ▼                     ▼
┌──────────────┐     ┌──────────────┐
│  SIP Server  │     │  CRM System  │
│  (PBX/ACD)   │     │  (Customer)  │
└──────────────┘     └──────────────┘
```

## Component Architecture

### Frontend Layer (Browser)

```
┌────────────────────────────────────────────────────────┐
│                   Browser Client                        │
├────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  HTML/CSS    │  │  JavaScript  │  │   SIP.js    │  │
│  │  (UI Layer)  │  │  (Business)  │  │  (WebRTC)   │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
│          │                 │                 │         │
│          └─────────────────┴─────────────────┘         │
│                           │                            │
└───────────────────────────┼────────────────────────────┘
                            │
                    ┌───────┴────────┐
                    │                │
                HTTPS/WSS         WSS
                    │                │
                    ▼                ▼
            ┌──────────────┐  ┌──────────────┐
            │  Flask API   │  │  SIP Server  │
            └──────────────┘  └──────────────┘
```

### Backend Layer (Flask)

```
┌────────────────────────────────────────────────────────┐
│                   Flask Application                     │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │              Call Center Blueprint             │   │
│  ├────────────────────────────────────────────────┤   │
│  │                                                 │   │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │   │
│  │  │  Routes  │  │  Models  │  │   Static    │  │   │
│  │  │  (API)   │  │  (ORM)   │  │ (Assets)    │  │   │
│  │  └──────────┘  └──────────┘  └─────────────┘  │   │
│  │       │              │              │          │   │
│  └───────┼──────────────┼──────────────┼──────────┘   │
│          │              │              │              │
│          ▼              ▼              ▼              │
│  ┌──────────────────────────────────────────────┐    │
│  │           SQLAlchemy (ORM)                   │    │
│  └──────────────────────────────────────────────┘    │
│                      │                                │
└──────────────────────┼────────────────────────────────┘
                       │
                       ▼
              ┌──────────────┐
              │  PostgreSQL  │
              └──────────────┘
```

### Database Schema

```
┌──────────────────────────────────────────────────────────┐
│                    Database Layer                        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐         ┌──────────────┐              │
│  │  cc_agents   │         │   cc_calls   │              │
│  ├──────────────┤         ├──────────────┤              │
│  │ id (PK)      │         │ id (PK)      │              │
│  │ agent_id     │         │ call_id      │              │
│  │ name         │    ┌───▶│ agent_id (FK)│              │
│  │ email        │    │    │ caller_number│              │
│  │ sip_username │    │    │ customer_id  │              │
│  │ sip_password │    │    │ state        │              │
│  │ sip_domain   │    │    │ started_at   │              │
│  │ state        │    │    │ ended_at     │              │
│  │ created_at   │    │    │ duration     │              │
│  └──────────────┘    │    └──────────────┘              │
│         │            │                                   │
│         │            │    ┌──────────────────────┐      │
│         │            │    │ cc_agent_activities  │      │
│         │            │    ├──────────────────────┤      │
│         │            │    │ id (PK)              │      │
│         └────────────┼───▶│ agent_id (FK)        │      │
│                      │    │ activity_type        │      │
│                      │    │ from_state           │      │
│                      │    │ to_state             │      │
│                      │    │ timestamp            │      │
│                      │    │ metadata             │      │
│                      │    └──────────────────────┘      │
│                      │                                   │
└──────────────────────┴───────────────────────────────────┘
```

## Call Flow Architecture

### Incoming Call Flow

```
    PSTN/VoIP Call
         │
         ▼
┌─────────────────┐
│   SIP Server    │  1. Call arrives at PBX
│   (Asterisk)    │
└────────┬────────┘
         │
         │ SIP INVITE
         ▼
┌─────────────────┐
│   ACD Engine    │  2. Route to available agent
│  (Call Router)  │
└────────┬────────┘
         │
         │ SIP INVITE (via WSS)
         ▼
┌─────────────────┐
│    Browser      │  3. Agent browser receives invite
│    (SIP.js)     │
└────────┬────────┘
         │
         │ onInvite event
         ▼
┌─────────────────┐
│  JavaScript     │  4. Trigger ringing event
│   Handler       │
└────────┬────────┘
         │
         ├─────────────────────┬─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌───────────────┐    ┌────────────────┐   ┌─────────────┐
│  Play Ring    │    │  Fetch Customer│   │   Update    │
│     Tone      │    │      Data      │   │   Backend   │
└───────────────┘    └────────────────┘   └─────────────┘
                              │                    │
                              ▼                    ▼
                     ┌────────────────┐   ┌─────────────┐
                     │  Show Popup    │   │  Create Call│
                     │   with Data    │   │   Record    │
                     └────────────────┘   └─────────────┘
                              │
                              ▼
                     ┌────────────────┐
                     │ Agent Decides  │
                     │ Answer/Reject  │
                     └────────────────┘
                              │
         ┌────────────────────┴─────────────────────┐
         │                                           │
         ▼                                           ▼
┌─────────────────┐                        ┌─────────────────┐
│  Answer Call    │                        │  Reject Call    │
│  (SIP ACCEPT)   │                        │  (SIP DECLINE)  │
└────────┬────────┘                        └────────┬────────┘
         │                                           │
         ▼                                           ▼
┌─────────────────┐                        ┌─────────────────┐
│ Establish Media │                        │   End Call      │
│   (WebRTC)      │                        └─────────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Active Call    │  5. Conversation
│   Connected     │
└─────────────────┘
```

### Outbound Call Flow

```
┌─────────────────┐
│   Agent UI      │  1. Agent enters number
│   (Dialpad)     │
└────────┬────────┘
         │
         │ Click "Call"
         ▼
┌─────────────────┐
│  JavaScript     │  2. Create SIP Inviter
│   makeCall()    │
└────────┬────────┘
         │
         │ SIP INVITE (via WSS)
         ▼
┌─────────────────┐
│  SIP Server     │  3. Route call to destination
└────────┬────────┘
         │
         │ Connect to PSTN/VoIP
         ▼
┌─────────────────┐
│   Destination   │  4. Ring destination
│     Number      │
└────────┬────────┘
         │
         │ Answer/Reject
         ▼
┌─────────────────┐
│  Active Call    │  5. Conversation
└─────────────────┘
```

## State Machine Architecture

### Agent State Transitions

```
         ┌──────────────┐
         │ Logged Out   │
         └──────┬───────┘
                │ Login
                ▼
         ┌──────────────┐
    ┌───│  Logged In   │
    │   └──────┬───────┘
    │          │ Ready
    │          ▼
    │   ┌──────────────┐         ┌──────────────┐
    │   │    Ready     │────────▶│   On Call    │
    │   └──────┬───────┘ Incoming└──────┬───────┘
    │          │          Call           │ Hangup
    │          │ Not Ready               │
    │          ▼                         │
    │   ┌──────────────┐                │
    └──▶│  Not Ready   │◀───────────────┘
        └──────────────┘
               │
               │ Logout
               ▼
        ┌──────────────┐
        │ Logged Out   │
        └──────────────┘
```

### Call State Transitions

```
    ┌──────────┐
    │   Idle   │
    └────┬─────┘
         │ New Call
         ▼
    ┌──────────┐
    │ Ringing  │
    └────┬─────┘
         │ Answer
         ▼
    ┌──────────┐         ┌──────────┐
    │Connected │────────▶│   Held   │
    └────┬─────┘  Hold   └────┬─────┘
         │                     │ Unhold
         │◀────────────────────┘
         │
         │ Hangup/Transfer
         ▼
    ┌──────────┐
    │  Ended   │
    └──────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Security Layers                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │            Transport Layer (TLS/SSL)           │    │
│  │  HTTPS (443) ────────── WSS (7443)             │    │
│  └────────────────────────────────────────────────┘    │
│                          │                              │
│  ┌────────────────────────────────────────────────┐    │
│  │         Application Layer Security             │    │
│  │  - Session Authentication                      │    │
│  │  - CSRF Protection                             │    │
│  │  - XSS Prevention                              │    │
│  │  - SQL Injection Prevention                    │    │
│  └────────────────────────────────────────────────┘    │
│                          │                              │
│  ┌────────────────────────────────────────────────┐    │
│  │           Media Layer Security                 │    │
│  │  - SRTP (Encrypted Audio)                      │    │
│  │  - DTLS for Key Exchange                       │    │
│  └────────────────────────────────────────────────┘    │
│                          │                              │
│  ┌────────────────────────────────────────────────┐    │
│  │           Data Layer Security                  │    │
│  │  - Password Hashing (bcrypt)                   │    │
│  │  - Encrypted Credentials                       │    │
│  │  - Database Encryption at Rest                 │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Integration Points

```
┌───────────────────────────────────────────────────────────┐
│                  Integration Architecture                  │
├───────────────────────────────────────────────────────────┤
│                                                            │
│   ┌──────────────┐                                        │
│   │ Call Center  │                                        │
│   │    Module    │                                        │
│   └──────┬───────┘                                        │
│          │                                                 │
│    ┌─────┴──────┬─────────┬──────────┬──────────┐        │
│    │            │         │          │          │        │
│    ▼            ▼         ▼          ▼          ▼        │
│ ┌──────┐   ┌──────┐  ┌──────┐  ┌───────┐  ┌───────┐    │
│ │ CRM  │   │ SIP  │  │Email │  │ SMS   │  │Ticket │    │
│ │System│   │Server│  │System│  │Gateway│  │System │    │
│ └──────┘   └──────┘  └──────┘  └───────┘  └───────┘    │
│                                                            │
│ Integration Methods:                                      │
│ • REST API                                                │
│ • WebSocket                                               │
│ • SIP Protocol                                            │
│ • SMTP                                                    │
│ • HTTP/HTTPS                                              │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Development Environment

```
┌────────────────────────────────────────┐
│        Development Setup               │
├────────────────────────────────────────┤
│                                        │
│  localhost:10000 (Flask Dev Server)   │
│         │                              │
│         ├─ /call-center/               │
│         ├─ /blog_project/              │
│         ├─ /sambanova/                 │
│         └─ /static/                    │
│                                        │
│  PostgreSQL (Local)                    │
│  SIP Server (Local/Remote)             │
│                                        │
└────────────────────────────────────────┘
```

### Production Environment

```
┌──────────────────────────────────────────────────────┐
│              Production Architecture                  │
├──────────────────────────────────────────────────────┤
│                                                       │
│         Internet                                      │
│            │                                          │
│            ▼                                          │
│   ┌─────────────────┐                                │
│   │  Load Balancer  │                                │
│   │   (NGINX/HAProxy)                                │
│   └────────┬────────┘                                │
│            │                                          │
│     ┌──────┴───────┬──────────┐                      │
│     │              │          │                      │
│     ▼              ▼          ▼                      │
│ ┌────────┐   ┌────────┐  ┌────────┐                 │
│ │ Flask  │   │ Flask  │  │ Flask  │                 │
│ │Instance│   │Instance│  │Instance│                 │
│ │   #1   │   │   #2   │  │   #3   │                 │
│ └───┬────┘   └───┬────┘  └───┬────┘                 │
│     │            │            │                      │
│     └────────────┴────────────┘                      │
│                  │                                    │
│                  ▼                                    │
│     ┌──────────────────────┐                         │
│     │  PostgreSQL Cluster  │                         │
│     │   (Primary+Replica)  │                         │
│     └──────────────────────┘                         │
│                                                       │
│     ┌──────────────────────┐                         │
│     │    Redis (Session    │                         │
│     │  & Cache Storage)    │                         │
│     └──────────────────────┘                         │
│                                                       │
│     ┌──────────────────────┐                         │
│     │   SIP Server Farm    │                         │
│     │   (HA Configuration) │                         │
│     └──────────────────────┘                         │
│                                                       │
└───────────────────────────────────────────────────────┘
```

## Technology Stack

```
┌────────────────────────────────────────────────────────┐
│                 Technology Stack                       │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Frontend:                                             │
│  ├─ HTML5 (Semantic markup)                            │
│  ├─ CSS3 (Modern styling, gradients, animations)       │
│  ├─ JavaScript ES6+ (Async/await, modules)             │
│  └─ SIP.js 0.21.2 (WebRTC/SIP client)                  │
│                                                         │
│  Backend:                                              │
│  ├─ Flask 2.x (Python web framework)                   │
│  ├─ SQLAlchemy (ORM)                                   │
│  ├─ Flask-Login (Session management)                   │
│  └─ Flask-SocketIO (WebSocket support)                 │
│                                                         │
│  Database:                                             │
│  ├─ PostgreSQL 12+ (Primary database)                  │
│  └─ Redis (Optional, for caching/sessions)             │
│                                                         │
│  SIP/VoIP:                                             │
│  ├─ SIP.js (Browser SIP client)                        │
│  ├─ WebRTC (Media handling)                            │
│  └─ Asterisk/FreeSWITCH (SIP server)                   │
│                                                         │
│  Infrastructure:                                       │
│  ├─ Gunicorn (WSGI server)                             │
│  ├─ Nginx (Reverse proxy)                              │
│  ├─ Let's Encrypt (SSL certificates)                   │
│  └─ Docker (Optional containerization)                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Performance Considerations

### Scalability

- **Horizontal Scaling**: Multiple Flask instances behind load balancer
- **Database Pooling**: Connection pooling for efficient DB access
- **Caching**: Redis for session and frequently accessed data
- **CDN**: Static assets served via CDN

### Optimization

- **WebSocket Persistence**: Sticky sessions for SIP connections
- **Database Indexing**: Indexed columns for fast queries
- **Lazy Loading**: Load data on-demand
- **Asset Minification**: Compressed CSS/JS for faster loading

---

*This architecture is designed for scalability, security, and reliability in production call center environments.*

