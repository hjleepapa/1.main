#!/usr/bin/env python3
"""
Environment Setup Script for Sambanova Project
Sets up Redis and Composio environment variables
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with all necessary environment variables"""
    env_content = """# Sambanova Environment Configuration
# Update these values with your actual credentials

# ===== DATABASE CONFIGURATION =====
DB_URI=postgresql://username:password@localhost:5432/database_name

# ===== FLASK CONFIGURATION =====
FLASK_KEY=your-secret-key-here

# ===== OPENAI CONFIGURATION =====
OPENAI_API_KEY=your-openai-api-key

# ===== SAMBANOVA CONFIGURATION =====
SAMBANOVA_API_KEY=your-sambanova-api-key

# ===== TWILIO CONFIGURATION =====
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# ===== WEBHOOK URLS (PRODUCTION) =====
WEBHOOK_BASE_URL=https://hjlees.com
WEBSOCKET_BASE_URL=wss://hjlees.com/sambanova_todo/ws

# ===== REDIS CONFIGURATION (NEW) =====
# Your Redis database details:
# Database Name: database-MH3YNEOB
# Subscription: database-MH3YNEOB
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# ===== COMPOSIO CONFIGURATION (NEW) =====
# Your Composio details:
# API Key: ak_68Xsj6WGv3Zl4ooBgkcD
# Project ID: pr_bz7nkY2wflSi
# Project Name: hjleegcti_workspace_first_project
COMPOSIO_API_KEY=ak_68Xsj6WGv3Zl4ooBgkcD
COMPOSIO_PROJECT_ID=pr_bz7nkY2wflSi

# ===== GOOGLE CALENDAR CONFIGURATION =====
GOOGLE_OAUTH2_TOKEN_B64=your-base64-encoded-oauth2-token

# ===== FREEPBX CONFIGURATION =====
FREEPBX_DOMAIN=34.26.59.14
FREEPBX_SIP_USERNAME=
FREEPBX_SIP_PASSWORD=
TRANSFER_TIMEOUT=30
SUPPORT_EXTENSION=2000
SALES_EXTENSION=2000
GENERAL_EXTENSION=2000
OPERATOR_EXTENSION=2000

# ===== SENTRY CONFIGURATION (OPTIONAL) =====
SENTRY_DSN=your-sentry-dsn-here

# ===== RATE LIMITING CONFIGURATION =====
# Flask-Limiter settings for Redis-based rate limiting
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
RATELIMIT_DEFAULT=10 per minute
"""
    
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with all environment variables")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def set_environment_variables():
    """Set environment variables for current session"""
    print("🔧 Setting environment variables...")
    
    # Redis configuration
    os.environ.setdefault('REDIS_HOST', 'localhost')
    os.environ.setdefault('REDIS_PORT', '6379')
    os.environ.setdefault('REDIS_PASSWORD', '')
    os.environ.setdefault('REDIS_DB', '0')
    
    # Composio configuration
    os.environ.setdefault('COMPOSIO_API_KEY', 'ak_68Xsj6WGv3Zl4ooBgkcD')
    os.environ.setdefault('COMPOSIO_PROJECT_ID', 'pr_bz7nkY2wflSi')
    
    # Rate limiting
    os.environ.setdefault('RATELIMIT_STORAGE_URL', 'redis://localhost:6379/1')
    os.environ.setdefault('RATELIMIT_DEFAULT', '10 per minute')
    
    print("✅ Environment variables set for current session")

def test_environment():
    """Test environment configuration"""
    print("🧪 Testing environment configuration...")
    
    try:
        from sambanova.environment_config import config
        
        # Print configuration summary
        config.print_config_summary()
        
        # Test Redis configuration
        redis_config = config.get_redis_config()
        print(f"🔴 Redis Config: {redis_config}")
        
        # Test Composio configuration
        composio_config = config.get_composio_config()
        print(f"🔗 Composio Config: {composio_config}")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Sambanova Environment Setup")
    print("=" * 50)
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        return False
    
    # Set environment variables
    set_environment_variables()
    
    # Test environment
    if test_environment():
        print("\n🎉 Environment setup complete!")
        print("\n📝 Next steps:")
        print("1. Update your .env file with actual credentials")
        print("2. Set your Redis host and password")
        print("3. Test the integrations: python3 sambanova/test_integrations.py")
        print("4. Start your Flask app")
        return True
    else:
        print("\n❌ Environment setup failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
