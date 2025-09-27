# Sambanova Twilio Configuration Guide

## 🌐 **Production Configuration (hjlees.com)**

### **Twilio Phone Number Settings:**

1. **Voice Webhook URL**: 
   ```
   https://hjlees.com/sambanova_todo/twilio/call
   ```
   - **Method**: POST
   - **Fallback URL**: Leave empty or use same URL

2. **Media Streams WebSocket URL** (if supported):
   ```
   wss://hjlees.com/sambanova_todo/ws
   ```

### **Required Routes on hjlees.com:**

The following routes must be accessible on your hjlees.com server:

- `POST /sambanova_todo/twilio/call` - Initial call handler
- `POST /sambanova_todo/twilio/process_audio` - Audio processing
- `GET /sambanova_todo/ws` - WebSocket endpoint (if using media streams)

## 🏠 **Local Development**

### **For Testing Locally:**

If you want to test locally, you would need to:

1. **Use ngrok** (temporary):
   ```bash
   ngrok start --all
   ```
   Then use the ngrok URLs in Twilio configuration

2. **Or configure Twilio for production** and deploy to hjlees.com

### **Local Server URLs:**
- Flask Server: `http://localhost:5000`
- WebSocket Server: `ws://localhost:5001`
- Web Interface: `http://localhost:5000/sambanova_todo/`

## 🚀 **Deployment Requirements**

### **For hjlees.com to work with Twilio:**

1. **SSL Certificate**: hjlees.com must have a valid SSL certificate
2. **WebSocket Support**: If using media streams, hjlees.com must support WebSocket connections
3. **Flask Application**: The Sambanova Flask app must be deployed and running on hjlees.com
4. **Port Configuration**: 
   - Main Flask app on port 80/443 (standard web ports)
   - WebSocket server on appropriate port (if separate)

### **Environment Variables on hjlees.com:**
```bash
WEBHOOK_BASE_URL=https://hjlees.com
WEBSOCKET_BASE_URL=wss://hjlees.com
SAMBANOVA_API_KEY=your_api_key_here
DB_URI=your_database_connection
# ... other required env vars
```

## 📞 **Twilio Configuration Steps:**

1. **Log into Twilio Console**
2. **Go to Phone Numbers > Manage > Active Numbers**
3. **Click on your phone number**
4. **In the Voice section:**
   - Webhook: `https://hjlees.com/sambanova_todo/twilio/call`
   - HTTP Method: POST
5. **In the Media Streams section (if using):**
   - WebSocket URL: `wss://hjlees.com/sambanova_todo/ws`
6. **Save Configuration**

## ⚠️ **Important Notes:**

- **No ngrok needed** when using hjlees.com
- **SSL required** for production webhooks
- **WebSocket support** needed for media streams
- **Flask app must be deployed** to hjlees.com
- **Environment variables** must be set on production server

## 🔧 **Troubleshooting:**

1. **Webhook not receiving calls**: Check SSL certificate and URL accessibility
2. **WebSocket connection failed**: Verify WebSocket support on hjlees.com
3. **Audio not working**: Ensure media streams are properly configured
4. **Database errors**: Verify DB_URI and database connectivity on hjlees.com
