# 🚀 Render.com Environment Variables Setup

This guide shows how to configure all environment variables for your Sambanova Hackathon project on Render.com.

## 📋 **REQUIRED ENVIRONMENT VARIABLES FOR RENDER**

### 🗄️ **Database Configuration**
```
DB_URI=postgresql://username:password@host:port/database_name
```
- **Purpose**: PostgreSQL database connection string
- **Render**: Use your Render PostgreSQL database URL
- **Example**: `postgresql://user:pass@dpg-abc123.oregon-postgres.render.com:5432/sambanova_db`

### 🔐 **Flask Configuration**
```
FLASK_KEY=your-secret-key-here
```
- **Purpose**: Flask secret key for sessions
- **Render**: Generate a strong random string
- **Example**: `sambanova-hackathon-2025-secret-key-abc123`

### 🤖 **OpenAI Configuration**
```
OPENAI_API_KEY=sk-your-openai-api-key
```
- **Purpose**: OpenAI API key for GPT-4 and Whisper
- **Render**: Your OpenAI API key
- **Example**: `sk-1234567890abcdef...`

### 🎯 **Sambanova Configuration**
```
SAMBANOVA_API_KEY=your-sambanova-api-key
```
- **Purpose**: Sambanova AI API key
- **Render**: Your Sambanova API key

## 📞 **TWILIO CONFIGURATION**

### Twilio Account (Required for Voice Calls)
```
TWILIO_ACCOUNT_SID=AC1234567890abcdef
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```
- **Purpose**: Twilio voice call handling
- **Render**: Your Twilio credentials
- **Example**: `TWILIO_ACCOUNT_SID=AC1234567890abcdef`

## 🌐 **WEBHOOK CONFIGURATION**

### Production URLs (Render-specific)
```
WEBHOOK_BASE_URL=https://your-app-name.onrender.com
WEBSOCKET_BASE_URL=wss://your-app-name.onrender.com/sambanova_todo/ws
```
- **Purpose**: Twilio webhook endpoints
- **Render**: Replace `your-app-name` with your actual Render app name
- **Example**: `WEBHOOK_BASE_URL=https://sambanova-hackathon.onrender.com`

## 🔴 **REDIS CONFIGURATION (NEW)**

### Your Redis Database Details
- **Database Name**: `database-MH3YNEOB`
- **Subscription**: `database-MH3YNEOB`

### Redis Environment Variables
```
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
```
- **Purpose**: Redis session storage and caching
- **Render**: Your Redis database credentials
- **Example**: `REDIS_HOST=dpg-abc123.oregon-redis.render.com`

## 🔗 **COMPOSIO CONFIGURATION (NEW)**

### Your Composio Details
- **API Key**: `ak_68Xsj6WGv3Zl4ooBgkcD`
- **Project ID**: `pr_bz7nkY2wflSi`
- **Project Name**: `hjleegcti_workspace_first_project`

### Composio Environment Variables
```
COMPOSIO_API_KEY=ak_68Xsj6WGv3Zl4ooBgkcD
COMPOSIO_PROJECT_ID=pr_bz7nkY2wflSi
```
- **Purpose**: External tool integrations (50+ tools)
- **Render**: Your Composio credentials

## 📅 **GOOGLE CALENDAR CONFIGURATION**

### OAuth2 Token
```
GOOGLE_OAUTH2_TOKEN_B64=your-base64-encoded-oauth2-token
```
- **Purpose**: Google Calendar integration
- **Render**: Base64-encoded OAuth2 token

## 📞 **FREEPBX CONFIGURATION**

### FreePBX Settings
```
FREEPBX_DOMAIN=34.26.59.14
FREEPBX_SIP_USERNAME=
FREEPBX_SIP_PASSWORD=
TRANSFER_TIMEOUT=30
SUPPORT_EXTENSION=2000
SALES_EXTENSION=2000
GENERAL_EXTENSION=2000
OPERATOR_EXTENSION=2000
```
- **Purpose**: Call transfer to FreePBX
- **Render**: Your FreePBX server configuration

## 📊 **SENTRY CONFIGURATION (OPTIONAL)**

### Error Monitoring
```
SENTRY_DSN=https://your-sentry-dsn
```
- **Purpose**: Error tracking and monitoring
- **Render**: Your Sentry DSN (optional)

## 🚦 **RATE LIMITING CONFIGURATION (NEW)**

### Redis-based Rate Limiting
```
RATELIMIT_STORAGE_URL=redis://user:pass@host:port/db
RATELIMIT_DEFAULT=10 per minute
```
- **Purpose**: DDoS protection for Twilio webhooks
- **Render**: Your Redis URL for rate limiting

## 🚀 **HOW TO ADD ENVIRONMENT VARIABLES IN RENDER**

### Method 1: Render Dashboard
1. Go to your Render dashboard
2. Select your Sambanova app
3. Go to "Environment" tab
4. Click "Add Environment Variable"
5. Add each variable with its value
6. Click "Save Changes"

### Method 2: Render CLI
```bash
# Install Render CLI
npm install -g @render/cli

# Login to Render
render login

# Set environment variables
render env set DB_URI=postgresql://user:pass@host:port/db
render env set OPENAI_API_KEY=sk-your-openai-key
render env set REDIS_HOST=your-redis-host
# ... add all variables
```

## 📝 **COMPLETE ENVIRONMENT VARIABLES LIST FOR RENDER**

Copy and paste these into your Render environment variables:

```bash
# Database
DB_URI=postgresql://username:password@host:port/database_name

# Flask
FLASK_KEY=your-secret-key-here

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Sambanova
SAMBANOVA_API_KEY=your-sambanova-api-key

# Twilio
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Webhooks (Update with your Render app name)
WEBHOOK_BASE_URL=https://your-app-name.onrender.com
WEBSOCKET_BASE_URL=wss://your-app-name.onrender.com/sambanova_todo/ws

# Redis (NEW)
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# Composio (NEW)
COMPOSIO_API_KEY=ak_68Xsj6WGv3Zl4ooBgkcD
COMPOSIO_PROJECT_ID=pr_bz7nkY2wflSi

# Google Calendar
GOOGLE_OAUTH2_TOKEN_B64=your-base64-encoded-oauth2-token

# FreePBX
FREEPBX_DOMAIN=34.26.59.14
FREEPBX_SIP_USERNAME=
FREEPBX_SIP_PASSWORD=
TRANSFER_TIMEOUT=30
SUPPORT_EXTENSION=2000
SALES_EXTENSION=2000
GENERAL_EXTENSION=2000
OPERATOR_EXTENSION=2000

# Sentry (Optional)
SENTRY_DSN=your-sentry-dsn-here

# Rate Limiting (NEW)
RATELIMIT_STORAGE_URL=redis://user:pass@host:port/db
RATELIMIT_DEFAULT=10 per minute
```

## 🔧 **RENDER-SPECIFIC CONFIGURATION**

### Update render.yaml
```yaml
services:
  - type: web
    name: sambanova-hackathon
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python start_sambanova_asgi.py
    envVars:
      - key: DB_URI
        fromDatabase:
          name: sambanova-db
          property: connectionString
      - key: REDIS_HOST
        fromService:
          type: redis
          name: sambanova-redis
          property: host
      - key: REDIS_PASSWORD
        fromService:
          type: redis
          name: sambanova-redis
          property: password
```

### Update start_sambanova_asgi.py
```python
import os
from sambanova.environment_config import config

# Print configuration summary on startup
config.print_config_summary()

# Rest of your startup code...
```

## 🧪 **TESTING ON RENDER**

### 1. **Deploy with Environment Variables**
- Add all environment variables in Render dashboard
- Deploy your app
- Check logs for configuration summary

### 2. **Test Redis Connection**
```bash
# In your Render app logs, look for:
✅ Redis connection established
✅ Session stored in Redis: session_id
```

### 3. **Test Composio Connection**
```bash
# In your Render app logs, look for:
✅ Composio connection test successful
✅ Loaded X Composio integration tools
```

### 4. **Test Voice Commands**
```
Call your Twilio number and say:
"Create a high-priority todo to review Redis integration, 
assign it to John, send a Slack message to the dev-team channel 
saying 'Redis integration is ready for review', and create a 
GitHub issue for the Redis implementation"
```

## 🎯 **HACKATHON DEMO ON RENDER**

### Perfect Demo Script:
1. **Show Environment Variables**: Display in Render dashboard
2. **Show Redis Integration**: Session persistence across restarts
3. **Show Composio Tools**: 50+ external integrations
4. **Show Voice Commands**: Multi-step workflows
5. **Show Real-time Features**: Team notifications

### Demo Flow:
```
1. "Create a todo for reviewing Redis integration"
2. "Assign it to John in the dev team"
3. "Send a Slack message to dev-team channel"
4. "Create a GitHub issue for Redis implementation"
5. "Show me my todos"
```

## 🔒 **SECURITY ON RENDER**

### Environment Variables Security
- ✅ **Never commit secrets** to your repository
- ✅ **Use Render's environment variables** for all secrets
- ✅ **Rotate API keys** regularly
- ✅ **Monitor usage** in Render dashboard

### Redis Security
- ✅ **Use Render Redis** (managed service)
- ✅ **Enable Redis AUTH** if available
- ✅ **Monitor Redis usage** in Render dashboard

## 📊 **MONITORING ON RENDER**

### Render Dashboard
- **Logs**: Check for Redis and Composio connection messages
- **Metrics**: Monitor CPU, memory, and request rates
- **Environment**: Verify all variables are set correctly

### Application Logs
Look for these success messages:
```
✅ Redis connection established
✅ Composio connection test successful
✅ Loaded X Composio integration tools
✅ Agent graph with Composio tools loaded successfully
```

## 🚀 **DEPLOYMENT CHECKLIST**

### Before Deployment
- [ ] All environment variables added to Render
- [ ] Redis database configured
- [ ] Composio API key set
- [ ] Twilio credentials configured
- [ ] Webhook URLs updated for Render

### After Deployment
- [ ] Check logs for Redis connection
- [ ] Check logs for Composio connection
- [ ] Test voice commands
- [ ] Test external integrations
- [ ] Monitor performance

---

**🎉 Your Sambanova project is now ready for Render.com deployment with Redis and Composio integrations!**

**Perfect for Hackathon success! 🏆**
