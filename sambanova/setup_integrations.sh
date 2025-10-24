#!/bin/bash
# Setup script for Redis and Composio integrations

echo "🚀 Setting up Redis and Composio integrations for Sambanova Hackathon project"
echo "=================================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cat > .env << EOF
# Sambanova Environment Configuration

# Database Configuration
DB_URI=postgresql://username:password@localhost:5432/database_name

# Flask Configuration
FLASK_KEY=your-secret-key-here

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Sambanova Configuration
SAMBANOVA_API_KEY=your-sambanova-api-key

# Twilio Configuration
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Webhook URLs (Production)
WEBHOOK_BASE_URL=https://hjlees.com
WEBSOCKET_BASE_URL=wss://hjlees.com/sambanova_todo/ws

# Redis Configuration (NEW)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Composio Configuration (NEW)
COMPOSIO_API_KEY=ak_68Xsj6WGv3Zl4ooBgkcD
COMPOSIO_PROJECT_ID=pr_bz7nkY2wflSi

# Google Calendar Configuration
GOOGLE_OAUTH2_TOKEN_B64=your-base64-encoded-oauth2-token

# Sentry Configuration (Optional)
SENTRY_DSN=your-sentry-dsn-here
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Add Redis environment variables if not present
if ! grep -q "REDIS_HOST" .env; then
    echo "📝 Adding Redis configuration to .env..."
    echo "" >> .env
    echo "# Redis Configuration" >> .env
    echo "REDIS_HOST=localhost" >> .env
    echo "REDIS_PORT=6379" >> .env
    echo "REDIS_PASSWORD=" >> .env
    echo "REDIS_DB=0" >> .env
    echo "✅ Redis configuration added"
fi

# Add Composio environment variables if not present
if ! grep -q "COMPOSIO_API_KEY" .env; then
    echo "📝 Adding Composio configuration to .env..."
    echo "" >> .env
    echo "# Composio Configuration" >> .env
    echo "COMPOSIO_API_KEY=ak_68Xsj6WGv3Zl4ooBgkcD" >> .env
    echo "COMPOSIO_PROJECT_ID=pr_bz7nkY2wflSi" >> .env
    echo "✅ Composio configuration added"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install redis>=5.0.0 composio-core>=0.3.0 flask-limiter>=3.0.0

# Test Redis connection
echo "🔴 Testing Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️ Redis is not running - start Redis with: redis-server"
    fi
else
    echo "⚠️ redis-cli not found - make sure Redis is installed"
fi

# Test Composio connection
echo "🔗 Testing Composio connection..."
python3 -c "
try:
    from sambanova.composio_tools import test_composio_connection
    if test_composio_connection():
        print('✅ Composio connection successful')
    else:
        print('❌ Composio connection failed')
except Exception as e:
    print(f'❌ Composio test failed: {e}')
"

# Run integration tests
echo "🧪 Running integration tests..."
python3 sambanova/test_integrations.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Update your .env file with actual Redis credentials"
echo "2. Configure your Redis database connection"
echo "3. Test the integrations: python3 sambanova/test_integrations.py"
echo "4. Start your Flask app and test voice commands"
echo ""
echo "🚀 Your Sambanova project now has Redis and Composio integrations!"
echo "📖 See REDIS_COMPOSIO_SETUP.md for detailed documentation"
