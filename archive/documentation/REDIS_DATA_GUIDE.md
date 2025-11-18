# Redis Data Storage Guide

## Overview
Redis is used for session management, caching, and real-time features in the Convonet project. Here's what data is stored and how to use it.

## Data Structure

### 1. Session Data (`session:{session_id}`)
**Purpose**: Store WebRTC voice assistant session information

**Data Fields**:
```json
{
  "authenticated": "True/False",
  "user_id": "123",
  "user_name": "John Doe", 
  "audio_buffer": "base64_encoded_audio_data",
  "is_recording": "True/False",
  "connected_at": "1698765432.123",
  "authenticated_at": "1698765432.456"
}
```

**Usage Examples**:
```python
# Get session data
session = get_session("abc123")
print(f"User: {session['user_name']}")
print(f"Recording: {session['is_recording']}")

# Update session
update_session("abc123", {
    "is_recording": "True",
    "audio_buffer": ""
})
```

### 2. User Cache (`user:{user_id}:{data_type}`)
**Purpose**: Cache user-specific data like todos, teams, etc.

**Data Types**:
- `todos`: User's todo items
- `teams`: User's team memberships
- `preferences`: User settings
- `activity`: Recent activity

**Usage Examples**:
```python
# Cache user todos
cache_user_data("123", "todos", todo_list, ttl=300)

# Get cached todos
todos = get_cached_user_data("123", "todos")

# Invalidate cache
invalidate_user_cache("123", "todos")
```

### 3. Team Notifications (`team:{team_id}:notifications`)
**Purpose**: Real-time team notifications via Pub/Sub

**Usage Examples**:
```python
# Publish team notification
notification = {
    "type": "todo_assigned",
    "message": "New todo assigned to you",
    "todo_id": "456"
}
publish_team_notification("team123", notification)
```

### 4. User Notifications (`user:{user_id}:notifications`)
**Purpose**: User-specific real-time notifications

**Usage Examples**:
```python
# Publish user notification
notification = {
    "type": "voice_message",
    "message": "Voice message received",
    "timestamp": time.time()
}
publish_user_notification("123", notification)
```

### 5. Rate Limiting (`rate_limit:{identifier}:{action}`)
**Purpose**: Prevent abuse and limit API calls

**Usage Examples**:
```python
# Check rate limit
key = get_rate_limit_key("user123", "voice_requests")
if check_rate_limit(key, limit=10, window=60):
    # Allow request
    pass
else:
    # Rate limit exceeded
    pass
```

### 6. Activity Tracking (`activity:{user_id}:{timestamp}`)
**Purpose**: Track user activity for analytics

**Usage Examples**:
```python
# Track activity
track_agent_activity("123", "voice_request", {
    "session_id": "abc123",
    "duration": 5.2
})

# Get user activity
activities = get_user_activity("123", hours=24)
```

## Debug Endpoints

### Check Session Data
```bash
GET /convonet_todo/webrtc/debug-session/{session_id}
```

**Response**:
```json
{
  "success": true,
  "session_id": "abc123",
  "data": {
    "authenticated": "True",
    "user_id": "123",
    "user_name": "John Doe",
    "is_recording": "False",
    "audio_buffer_length": 137894,
    "audio_buffer_preview": "GkXfo59ChoEBQveBAULygQRC84EIQoKEd2VibUKHgQRChYECGFOAZwH...",
    "decoded_audio_length": 137894,
    "base64_valid": true
  },
  "storage": "redis"
}
```

### Clear Session Data
```bash
GET /convonet_todo/webrtc/clear-session/{session_id}
```

## Redis Commands

### Direct Redis Access
```python
from convonet.redis_manager import redis_manager

# Check if Redis is available
if redis_manager.is_available():
    # Get all session keys
    session_keys = redis_manager.redis_client.keys("session:*")
    
    # Get specific session
    session_data = redis_manager.redis_client.hgetall("session:abc123")
    
    # Get all user cache keys
    cache_keys = redis_manager.redis_client.keys("user:*")
    
    # Get Redis info
    info = redis_manager.redis_client.info()
    print(f"Redis memory usage: {info['used_memory_human']}")
```

### Monitor Real-time Data
```python
# Subscribe to team notifications
pubsub = redis_manager.redis_client.pubsub()
pubsub.subscribe("team:123:notifications")

for message in pubsub.listen():
    if message['type'] == 'message':
        notification = json.loads(message['data'])
        print(f"Team notification: {notification}")
```

## Data Lifecycle

### Session Lifecycle
1. **Create**: When WebRTC client connects
2. **Update**: During authentication, recording, audio processing
3. **Extend**: TTL extended on activity (1 hour default)
4. **Delete**: When client disconnects or TTL expires

### Cache Lifecycle
1. **Create**: When data is first requested
2. **Update**: When underlying data changes
3. **Invalidate**: When data becomes stale
4. **Expire**: TTL-based expiration (5 minutes default)

## Monitoring

### Redis Health Check
```python
# Check Redis connection
if redis_manager.is_available():
    print("✅ Redis is available")
    # Test basic operations
    redis_manager.redis_client.ping()
    print("✅ Redis ping successful")
else:
    print("❌ Redis is unavailable")
```

### Memory Usage
```python
# Get Redis memory usage
info = redis_manager.redis_client.info()
print(f"Used memory: {info['used_memory_human']}")
print(f"Max memory: {info['maxmemory_human']}")
print(f"Memory usage: {info['used_memory_percentage']}%")
```

### Key Statistics
```python
# Count different key types
session_count = len(redis_manager.redis_client.keys("session:*"))
user_cache_count = len(redis_manager.redis_client.keys("user:*"))
activity_count = len(redis_manager.redis_client.keys("activity:*"))

print(f"Sessions: {session_count}")
print(f"User caches: {user_cache_count}")
print(f"Activities: {activity_count}")
```

## Best Practices

### 1. Session Management
- Always check if Redis is available before operations
- Use appropriate TTL for different data types
- Clean up sessions on disconnect

### 2. Caching Strategy
- Cache frequently accessed data
- Use appropriate cache invalidation
- Monitor cache hit rates

### 3. Error Handling
- Always have fallback mechanisms
- Log Redis operations for debugging
- Handle connection failures gracefully

### 4. Performance
- Use Redis pipelining for bulk operations
- Monitor memory usage
- Set appropriate TTL values

## Troubleshooting

### Common Issues
1. **Redis Connection Failed**: Check environment variables
2. **Session Not Found**: Check TTL and session ID
3. **Memory Issues**: Monitor Redis memory usage
4. **Slow Operations**: Check Redis performance metrics

### Debug Commands
```bash
# Check Redis connection
redis-cli ping

# List all keys
redis-cli keys "*"

# Get specific session
redis-cli hgetall "session:abc123"

# Monitor Redis commands
redis-cli monitor
```

## Environment Variables

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password
REDIS_DB=0
```

## Integration with Other Services

### Sentry Integration
- All Redis operations are tracked in Sentry
- Errors are automatically captured
- Performance metrics are monitored

### WebRTC Integration
- Session data is shared between WebRTC and Redis
- Audio buffers are stored in Redis
- Real-time updates via Socket.IO

### Agent Integration
- User context is cached in Redis
- Activity is tracked for analytics
- Rate limiting prevents abuse
