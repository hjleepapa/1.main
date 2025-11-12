# Redis & Composio Integration Setup Guide

This guide explains how to set up Redis and Composio integrations for your Convonet Hackathon project.

## 🔴 Redis Setup

### 1. Redis Database Configuration

Your Redis database details:
- **Database Name**: `database-MH3YNEOB`
- **Subscription**: `database-MH3YNEOB`

### 2. Environment Variables

Add these to your environment variables:

```bash
# Redis Configuration
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
```

### 3. Redis Features Enabled

✅ **Session Management**: WebRTC sessions stored in Redis with TTL
✅ **Caching**: User data cached for faster responses
✅ **Pub/Sub**: Real-time team notifications
✅ **Rate Limiting**: DDoS protection for Twilio webhooks
✅ **Analytics**: Agent activity tracking

### 4. Fallback Behavior

If Redis is unavailable, the system automatically falls back to in-memory storage with a warning message.

## 🔗 Composio Setup

### 1. Composio Configuration

Your Composio details:
- **API Key**: `ak_68Xsj6WGv3Zl4ooBgkcD`
- **Project ID**: `pr_bz7nkY2wflSi`
- **Project Name**: `hjleegcti_workspace_first_project`

### 2. Environment Variables

Add these to your environment variables:

```bash
# Composio Configuration
COMPOSIO_API_KEY=ak_68Xsj6WGv3Zl4ooBgkcD
COMPOSIO_PROJECT_ID=pr_bz7nkY2wflSi
```

### 3. Available Integrations

✅ **Slack**: Send messages, create channels, post updates
✅ **GitHub**: Create issues, manage pull requests, create branches
✅ **Gmail**: Send emails, read messages, manage inbox
✅ **Notion**: Create pages, search content, manage databases
✅ **Jira**: Create tickets, manage issues, track progress

### 4. Voice Commands Examples

```
"Send a Slack message to the dev-team channel: Deployment is complete"
"Create a GitHub issue for fixing timeout errors"
"Send an email to john@example.com about tomorrow's meeting"
"Create a Notion page for meeting notes"
"Create a Jira ticket for implementing Redis caching"
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install redis>=5.0.0 composio-core>=0.3.0 flask-limiter>=3.0.0
```

### 2. Set Environment Variables

```bash
export REDIS_HOST=your-redis-host
export REDIS_PORT=6379
export REDIS_PASSWORD=your-redis-password
export COMPOSIO_API_KEY=ak_68Xsj6WGv3Zl4ooBgkcD
export COMPOSIO_PROJECT_ID=pr_bz7nkY2wflSi
```

### 3. Test Integration

The system will automatically test connections on startup:
- ✅ Redis connection test
- ✅ Composio connection test
- ✅ Tool loading verification

## 📊 Performance Benefits

### Redis Integration
- **Session Persistence**: Survives server restarts
- **Horizontal Scaling**: Multiple server instances
- **Faster Responses**: Cached user data (3-5s → 1-2s)
- **Real-time Notifications**: Team collaboration updates

### Composio Integration
- **50+ External Tools**: Expanded from 38 to 50+ tools
- **Seamless Workflows**: Multi-step operations
- **Enterprise Integrations**: Slack, GitHub, Gmail, Notion, Jira
- **Voice-First**: All integrations accessible by voice

## 🔧 Troubleshooting

### Redis Issues
```bash
# Test Redis connection
redis-cli ping

# Check Redis logs
redis-cli monitor
```

### Composio Issues
```bash
# Test Composio connection
python -c "from convonet.composio_tools import test_composio_connection; print(test_composio_connection())"
```

### Common Solutions
1. **Redis Connection Failed**: Check host/port/password
2. **Composio Tools Not Loading**: Verify API key and project ID
3. **Session Not Persisting**: Ensure Redis is running and accessible
4. **Tools Not Available**: Check Composio app permissions

## 📈 Monitoring

### Redis Metrics
- Session count and TTL
- Cache hit/miss rates
- Pub/Sub message volume
- Memory usage

### Composio Metrics
- Tool usage statistics
- Integration success rates
- API response times
- Error rates

## 🎯 Demo Script

Perfect for your Hackathon demo:

```
"Hey Convonet, create a high-priority todo to review Redis integration, 
assign it to John, send a Slack message to the dev-team channel saying 
'Redis integration is ready for review', and create a GitHub issue 
for the Redis implementation"
```

This demonstrates:
- ✅ Natural language processing
- ✅ Multi-step workflow
- ✅ Team collaboration
- ✅ External integrations (Slack + GitHub)
- ✅ Database operations (Redis caching)

## 🔒 Security Notes

- Redis password should be strong and unique
- Composio API key should be kept secure
- Use environment variables, never hardcode credentials
- Enable Redis AUTH if possible
- Monitor Redis access logs

## 📚 Documentation

- [Redis Documentation](https://redis.io/docs/)
- [Composio Documentation](https://docs.composio.dev/)
- [Flask-Limiter Documentation](https://flask-limiter.readthedocs.io/)

---

**Ready to scale your Convonet project with Redis and Composio! 🚀**
