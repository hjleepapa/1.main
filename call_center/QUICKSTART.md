# Call Center Module - Quick Start Guide

Get your SIP-based call center up and running in minutes!

## Prerequisites

- ✅ PostgreSQL database configured
- ✅ Flask application running
- ✅ SIP server (Asterisk, FreeSWITCH, or similar) with WebSocket support

## Step 1: Initialize Database

Run the database initialization script:

```bash
cd "/Users/hj/Web Development Projects/1. Main"
python call_center/init_db.py
```

This will:
- Create necessary database tables (`cc_agents`, `cc_calls`, `cc_agent_activities`)
- Optionally create a test agent for initial testing

## Step 2: Configure SIP Server

### Option A: Using Asterisk

1. Enable WebSocket support in `/etc/asterisk/http.conf`:
   ```ini
   [general]
   enabled=yes
   bindaddr=0.0.0.0
   bindport=8088
   ```

2. Configure WebSocket transport in `/etc/asterisk/pjsip.conf`:
   ```ini
   [transport-wss]
   type=transport
   protocol=wss
   bind=0.0.0.0:7443
   ```

3. Create SIP endpoints for your agents:
   ```ini
   [agent001]
   type=endpoint
   context=default
   disallow=all
   allow=ulaw
   aors=agent001
   auth=agent001
   
   [agent001]
   type=aor
   max_contacts=1
   
   [agent001]
   type=auth
   auth_type=userpass
   username=agent001
   password=your_password
   ```

### Option B: Using FreeSWITCH

1. Enable Verto (WebRTC) in `autoload_configs/verto.conf.xml`
2. Configure your SIP profiles to support WebRTC
3. Create user accounts in the directory

### Option C: Cloud SIP Provider

Use a cloud SIP provider like:
- Twilio Programmable Voice
- Vonage (formerly Nexmo)
- Plivo
- Bandwidth

## Step 3: Start Your Flask Application

```bash
cd "/Users/hj/Web Development Projects/1. Main"
python app.py
```

Or if using Gunicorn:
```bash
gunicorn -k eventlet -w 1 --bind 0.0.0.0:10000 app:app
```

## Step 4: Access the Call Center

Open your browser and navigate to:

```
http://localhost:10000/call-center/
```

Or if deployed:
```
https://your-domain.com/call-center/
```

## Step 5: Login as an Agent

### Using Test Agent (if created during init):

- **Agent ID**: `agent001`
- **Name**: `Test Agent`
- **SIP Username**: `agent001`
- **SIP Password**: `test123`
- **SIP Domain**: `your-sip-server.com` (e.g., `sip.example.com`)
- **Extension**: `1001`

### Creating a New Agent:

Agents are automatically created on first login. Just enter the credentials that match your SIP server configuration.

## Step 6: Agent Workflow

1. **Login** with your SIP credentials
2. **Set Status to Ready** to receive calls
3. **Answer incoming calls** - customer popup will appear automatically
4. **Use call controls**:
   - Hold/Unhold
   - Transfer
   - Hangup
5. **Make outbound calls** using the dialpad
6. **Set Not Ready** when taking breaks
7. **Logout** when done

## Testing Without a SIP Server

If you want to test the UI without a real SIP server:

1. Comment out the SIP connection code in `call_center/static/js/call_center.js`:
   ```javascript
   // Temporarily disable SIP for UI testing
   // this.initSIPClient(data.sip_username, data.sip_password, data.sip_domain);
   ```

2. You can still test:
   - Login/logout flow
   - Agent status changes (Ready/Not Ready)
   - UI interactions
   - Customer popup (simulated)

## Troubleshooting

### Issue: Cannot connect to SIP server

**Solution:**
- Verify SIP server is running and accessible
- Check WebSocket port (usually 7443 or 8088)
- Ensure SSL/TLS certificates are valid
- Check firewall rules

### Issue: No audio during calls

**Solution:**
- Grant browser microphone permissions
- Check STUN/TURN server configuration
- Verify WebRTC is enabled in your SIP server
- Test with headphones to avoid echo

### Issue: Customer popup doesn't show

**Solution:**
- Check browser console for JavaScript errors
- Verify API endpoint is accessible
- Check CORS configuration if using different domains

### Issue: Database errors

**Solution:**
- Verify PostgreSQL is running
- Check DB_URI environment variable
- Ensure database user has CREATE permissions
- Run migrations if needed

## Next Steps

### Production Deployment

1. **Enable HTTPS** - Required for WebRTC
   ```bash
   # Use Let's Encrypt for free SSL
   sudo certbot --nginx -d your-domain.com
   ```

2. **Configure Reverse Proxy** (Nginx example):
   ```nginx
   location /call-center/ {
       proxy_pass http://localhost:10000;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
   }
   ```

3. **Enable Session Security**:
   - Use strong SECRET_KEY
   - Enable HTTPS-only cookies
   - Implement CSRF protection

4. **Monitor Performance**:
   - Set up logging
   - Monitor database performance
   - Track call metrics

### Integration

1. **Connect to Your CRM**:
   - Update `get_customer_data()` in `routes.py`
   - Fetch real customer information
   - Display relevant data in popup

2. **Add Call Recording**:
   - Configure your SIP server for recording
   - Store recordings in cloud storage
   - Link recordings to call records

3. **Implement Call Analytics**:
   - Track call duration
   - Monitor agent performance
   - Generate reports

4. **Add More Features**:
   - Conference calling
   - Call queues
   - IVR integration
   - Voicemail

## Support & Documentation

- Full documentation: `call_center/README.md`
- Database models: `call_center/models.py`
- API routes: `call_center/routes.py`
- Frontend code: `call_center/static/js/call_center.js`

## Tips for Success

✅ **Start Simple**: Test with one agent first
✅ **Use Test Calls**: Make test calls to verify everything works
✅ **Check Logs**: Monitor Flask logs and browser console
✅ **Secure Everything**: Use HTTPS in production
✅ **Document**: Keep track of your SIP server configuration

Happy calling! 📞

