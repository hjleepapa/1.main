# Call Center Module

A comprehensive SIP-based call center UI client with ACD (Automatic Call Distribution) features, built with Flask and SIP.js.

## Features

### ACD Call Center Features
- **Agent Login/Logout**: Secure agent authentication with SIP credentials
- **Agent Ready/Not Ready**: Control agent availability for receiving calls
- **Real-time Agent Status**: Track current agent state and time in status
- **Call Queuing**: Support for incoming call distribution

### Phone Handling Functions
- **Event Ringing**: Detect and handle incoming call events
- **Request Answer**: Accept incoming calls
- **Request Drop Call**: Hang up active calls
- **Call Transfer**: Support for blind and attended call transfers
- **Call Hold/Unhold**: Put calls on hold and resume
- **Outbound Calling**: Dialpad for making outbound calls

### Customer Experience
- **Customer Data Popup**: Automatic popup of customer information when calls ring
- **CRM Integration Ready**: API endpoint for fetching customer data
- **Call History**: Track recent calls and interactions

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **SIP Client**: SIP.js (browser-based SIP client)
- **Database**: PostgreSQL (via SQLAlchemy)
- **Real-time**: WebSockets for SIP signaling

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL database
- SIP server (e.g., Asterisk, FreeSWITCH, or any SIP PBX)
- SSL certificate (required for WebRTC/WSS connections)

### Setup

1. **Install Dependencies**
   ```bash
   pip install flask flask-sqlalchemy psycopg2-binary
   ```

2. **Configure Database**
   
   The module uses your existing database configuration from `DB_URI` environment variable.
   
   ```bash
   export DB_URI="postgresql://username:password@localhost/dbname"
   ```

3. **Initialize Database Tables**
   
   ```bash
   python -c "from app import app; from extensions import db; from call_center.models import Agent, Call, AgentActivity; app.app_context().push(); db.create_all()"
   ```

4. **Configure SIP Server**
   
   Update your SIP server to support:
   - WebSocket transport (WSS)
   - CORS headers for browser access
   - SIP over WebRTC (required for browser-based clients)

## Usage

### Access the Call Center Dashboard

Navigate to: `http://your-domain/call-center/`

### Agent Login

1. Enter your credentials:
   - Agent ID
   - Name
   - SIP Username
   - SIP Password
   - SIP Domain (your SIP server address)
   - Extension

2. Click "Login"

### Agent Workflow

1. **Set Status to Ready**
   - Click the "Ready" button to make yourself available for calls

2. **Receive Incoming Calls**
   - When a call rings, a customer popup will appear
   - Review customer information
   - Click "Answer" to accept the call

3. **Handle Active Calls**
   - Hold/Unhold calls
   - Transfer calls (blind or attended)
   - Hang up when done

4. **Make Outbound Calls**
   - Use the dialpad to enter a number
   - Click "Call" to initiate

5. **Set Status to Not Ready**
   - Click "Not Ready" when taking a break
   - Provide a reason (e.g., "Break", "Lunch")

6. **Logout**
   - Click "Logout" when ending your shift

## API Endpoints

### Agent Management

- `POST /call-center/api/agent/login` - Agent login
- `POST /call-center/api/agent/logout` - Agent logout
- `POST /call-center/api/agent/ready` - Set agent ready
- `POST /call-center/api/agent/not-ready` - Set agent not ready
- `GET /call-center/api/agent/status` - Get current agent status

### Call Handling

- `POST /call-center/api/call/ringing` - Incoming call event
- `POST /call-center/api/call/answer` - Answer call
- `POST /call-center/api/call/drop` - Drop/hang up call
- `POST /call-center/api/call/transfer` - Transfer call
- `POST /call-center/api/call/hold` - Hold call
- `POST /call-center/api/call/unhold` - Unhold call

### Customer Data

- `GET /call-center/api/customer/<customer_id>` - Get customer information

## SIP Server Configuration

### Asterisk Example

Add to `http.conf`:
```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
tlsenable=yes
tlsbindaddr=0.0.0.0:8089
tlscertfile=/path/to/cert.pem
tlsprivatekey=/path/to/key.pem
```

Add to `pjsip.conf`:
```ini
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0:7443
external_media_address=YOUR_PUBLIC_IP
external_signaling_address=YOUR_PUBLIC_IP
```

### FreeSWITCH Example

Add to `verto.conf.xml`:
```xml
<param name="bind-local" value="0.0.0.0:8081"/>
<param name="bind-local-wss" value="0.0.0.0:8082"/>
<param name="secure-combined" value="/path/to/wss.pem"/>
```

## Database Schema

### Tables

- **cc_agents**: Agent information and SIP credentials
- **cc_calls**: Call records and history
- **cc_agent_activities**: Agent activity log

## Customization

### Customer Data Integration

Modify the `get_customer_data()` function in `routes.py` to integrate with your CRM:

```python
@call_center_bp.route('/api/customer/<customer_id>', methods=['GET'])
def get_customer_data(customer_id):
    # Replace with your CRM API call
    customer = your_crm_api.get_customer(customer_id)
    return jsonify(customer)
```

### UI Customization

- CSS: `call_center/static/css/call_center.css`
- HTML: `call_center/templates/call_center.html`
- JavaScript: `call_center/static/js/call_center.js`

## Troubleshooting

### SIP Connection Issues

1. **Check SIP Server WebSocket Support**
   - Ensure WSS (WebSocket Secure) is enabled
   - Verify SSL certificates are valid

2. **Browser Console Errors**
   - Open browser developer tools
   - Check for SIP.js connection errors
   - Verify SIP credentials

3. **CORS Issues**
   - Configure SIP server to allow CORS from your domain
   - Add appropriate Access-Control headers

### Audio Issues

1. **No Audio on Calls**
   - Check browser microphone permissions
   - Verify STUN/TURN server configuration
   - Ensure firewall allows RTP traffic

2. **Echo or Feedback**
   - Use headset instead of speakers
   - Check echo cancellation settings

## Production Deployment

### Security Checklist

- [ ] Use HTTPS for all connections
- [ ] Enable WSS (WebSocket Secure) on SIP server
- [ ] Implement rate limiting on API endpoints
- [ ] Store SIP passwords securely (hashed)
- [ ] Use session management with secure cookies
- [ ] Enable CSRF protection
- [ ] Implement proper authentication and authorization
- [ ] Use environment variables for sensitive configuration

### Performance Optimization

- Use Redis for session storage
- Implement connection pooling for database
- Enable caching for customer data
- Use CDN for static assets
- Monitor and log all call events

## License

This module is part of your main Flask application.

## Support

For issues or questions, please refer to the main project documentation or contact your system administrator.

