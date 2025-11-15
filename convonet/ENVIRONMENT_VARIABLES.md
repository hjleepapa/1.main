# 🔧 Environment Variables Configuration

This document lists all environment variables needed for the Convonet Hackathon project, including the new Redis and Composio integrations.

## 📋 **REQUIRED ENVIRONMENT VARIABLES**

### 🗄️ **Database Configuration**
```bash
DB_URI=postgresql://username:password@localhost:5432/database_name
```
- **Purpose**: PostgreSQL database connection string
- **Format**: `postgresql://username:password@host:port/database`
- **Example**: `postgresql://user:pass@localhost:5432/convonet_db`

### 🔐 **Flask Configuration**
```bash
FLASK_KEY=your-secret-key-here
```
- **Purpose**: Flask secret key for sessions and security
- **Format**: Random string (32+ characters recommended)
- **Example**: `your-super-secret-flask-key-here`

### 🤖 **OpenAI Configuration**
```bash
OPENAI_API_KEY=your-openai-api-key
```
- **Purpose**: OpenAI API key for GPT-4 and Whisper
- **Format**: `sk-...` (OpenAI API key format)
- **Example**: `sk-1234567890abcdef...`

### 🎯 **Convonet Configuration**
```bash
CONVONET_API_KEY=your-convonet-api-key
```
- **Purpose**: Convonet AI API key
- **Format**: Your Convonet API key
- **Example**: `convonet-api-key-here`

## 📞 **TWILIO CONFIGURATION**

### Twilio Account
```bash
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
```
- **Purpose**: Twilio voice call handling
- **Format**: 
  - `TWILIO_ACCOUNT_SID`: `AC...` (Twilio Account SID)
  - `TWILIO_AUTH_TOKEN`: Random string (Twilio Auth Token)
  - `TWILIO_PHONE_NUMBER`: `+1234567890` (Phone number format)

## 🌐 **WEBHOOK CONFIGURATION**

### Production URLs
```bash
WEBHOOK_BASE_URL=https://hjlees.com
WEBSOCKET_BASE_URL=wss://hjlees.com/convonet_todo/ws
```
- **Purpose**: Twilio webhook endpoints
- **Format**: HTTPS URLs for production
- **Example**: `https://your-domain.com`

## 🔴 **REDIS CONFIGURATION (NEW)**

### Your Redis Database Details
- **Database Name**: `database-MH3YNEOB`
- **Subscription**: `database-MH3YNEOB`

### Redis Environment Variables
```bash
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
```
- **Purpose**: Redis session storage and caching
- **Format**:
  - `REDIS_HOST`: Redis server hostname/IP
  - `REDIS_PORT`: Redis port (default: 6379)
  - `REDIS_PASSWORD`: Redis password (if required)
  - `REDIS_DB`: Redis database number (0-15)

### Redis Features Enabled
- ✅ **Session Management**: WebRTC sessions with TTL
- ✅ **Caching**: User data for faster responses
- ✅ **Pub/Sub**: Real-time team notifications
- ✅ **Rate Limiting**: DDoS protection
- ✅ **Analytics**: Agent activity tracking

## 🛡️ **FRONTEGG / FRONTMCP CONFIGURATION (NEW)**

```bash
FRONTEGG_CLIENT_ID=your-frontegg-client-id
FRONTEGG_CLIENT_SECRET=your-frontegg-client-secret
FRONTEGG_BASE_URL=https://your-workspace.frontegg.com
FRONTEGG_JWKS_URL=https://your-workspace.frontegg.com/.well-known/jwks.json
FRONTEGG_AUDIENCE=your-frontegg-client-id
FRONTEGG_ISSUER=https://your-workspace.frontegg.com
FRONTEGG_DEFAULT_TEAM_ID=uuid-of-existing-convonet-team
```

- **Purpose**: Enable FrontMCP (Frontegg) Auth-as-a-Service for the hackathon.
- **Source**: Copy the values from the Frontegg integration guide (`https://portal.frontegg.com/development/frontegg-integration-guide`).
- **Default team**: Assign the UUID of the Convonet team that should own SSO users; the backend will auto-create memberships if missing.

## 🔗 **COMPOSIO CONFIGURATION (NEW)**

### Your Composio Details
- **API Key**: `ak_68Xsj6WGv3Zl4ooBgkcD`
- **Project ID**: `pr_bz7nkY2wflSi`
- **Project Name**: `hjleegcti_workspace_first_project`

### Composio Environment Variables
```bash
COMPOSIO_API_KEY=ak_68Xsj6WGv3Zl4ooBgkcD
COMPOSIO_PROJECT_ID=pr_bz7nkY2wflSi
```
- **Purpose**: External tool integrations
- **Format**: Composio API credentials
- **Features**: 50+ external tools (Slack, GitHub, Gmail, Notion, Jira)

## 📅 **GOOGLE CALENDAR CONFIGURATION**

### OAuth2 Token
```bash
GOOGLE_OAUTH2_TOKEN_B64=your-base64-encoded-oauth2-token
```
- **Purpose**: Google Calendar integration
- **Format**: Base64-encoded OAuth2 token
- **Example**: `eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...`

## 📞 **FREEPBX CONFIGURATION**

### FreePBX Settings
```bash
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
- **Format**: SIP server configuration
- **Example**: `FREEPBX_DOMAIN=your-freepbx-ip`

## 📊 **SENTRY CONFIGURATION (OPTIONAL)**

### Error Monitoring
```bash
SENTRY_DSN=your-sentry-dsn-here
```
- **Purpose**: Error tracking and monitoring
- **Format**: Sentry DSN URL
- **Example**: `https://abc123@o123456.ingest.sentry.io/123456`

## 🚦 **RATE LIMITING CONFIGURATION (NEW)**

### Redis-based Rate Limiting
```bash
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
RATELIMIT_DEFAULT=10 per minute
```
- **Purpose**: DDoS protection for Twilio webhooks
- **Format**: Redis URL for rate limiting storage
- **Example**: `redis://user:pass@host:port/db`

## 🚀 **QUICK SETUP**

### 1. **Create .env File**
```bash
cd convonet
python3 setup_environment.py
```

### 2. **Update with Your Credentials**
Edit the `.env` file with your actual values:
```bash
# Update these with your actual credentials
DB_URI=postgresql://your_user:your_pass@your_host:5432/your_db
OPENAI_API_KEY=sk-your-actual-openai-key
REDIS_HOST=your-actual-redis-host
REDIS_PASSWORD=your-actual-redis-password
```

### 3. **Test Configuration**
```bash
python3 convonet/test_integrations.py
```

## 🔧 **ENVIRONMENT CONFIGURATION CLASS**

The project includes a centralized configuration class:

```python
from convonet.environment_config import config

# Access configuration
redis_config = config.get_redis_config()
composio_config = config.get_composio_config()

# Print configuration summary
config.print_config_summary()
```

## 🧪 **TESTING ENVIRONMENT**

### Test Script
```bash
python3 convonet/test_integrations.py
```

### Manual Testing
```python
from convonet.environment_config import config

# Check required variables
missing = config.validate_required_vars()
if missing:
    print(f"Missing: {missing}")
else:
    print("All required variables configured")
```

## 🔒 **SECURITY NOTES**

### Environment Variables Security
- ✅ **Never commit .env files** to version control
- ✅ **Use strong passwords** for Redis and database
- ✅ **Rotate API keys** regularly
- ✅ **Use environment-specific values** (dev/staging/prod)

### Redis Security
- ✅ **Enable Redis AUTH** if possible
- ✅ **Use strong passwords**
- ✅ **Restrict network access**
- ✅ **Monitor access logs**

### Composio Security
- ✅ **Keep API keys secure**
- ✅ **Use environment variables**
- ✅ **Monitor API usage**
- ✅ **Rotate keys regularly**

## 📚 **DOCUMENTATION**

- `environment_config.py` - Centralized configuration management
- `setup_environment.py` - Automated environment setup
- `test_integrations.py` - Integration testing
- `REDIS_COMPOSIO_SETUP.md` - Detailed setup guide

## 🎯 **HACKATHON DEMO**

Perfect environment setup for your Hackathon demo:

```bash
# Set your Redis credentials
export REDIS_HOST=your-redis-host
export REDIS_PASSWORD=your-redis-password

# Set your OpenAI key
export OPENAI_API_KEY=sk-your-openai-key

# Test everything
python3 convonet/test_integrations.py
```

---

**🚀 Your Convonet project is now configured with Redis and Composio integrations!**

**Ready for Hackathon success! 🏆**
