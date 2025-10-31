"""
Environment Configuration for Sambanova Project
Handles Redis and Composio environment variables
"""

import os
from typing import Optional

def safe_int(value: str, default: int = 0) -> int:
    """Safely convert string to int with fallback"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

class EnvironmentConfig:
    """Environment configuration manager for Sambanova project"""
    
    # Database Configuration
    DB_URI: str = os.getenv('DB_URI', 'postgresql://username:password@localhost:5432/database_name')
    
    # Flask Configuration
    FLASK_KEY: str = os.getenv('FLASK_KEY', 'your-secret-key-here')
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    
    # Sambanova Configuration
    SAMBANOVA_API_KEY: str = os.getenv('SAMBANOVA_API_KEY', '')
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN: str = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER: str = os.getenv('TWILIO_PHONE_NUMBER', '')
    
    # Webhook URLs
    WEBHOOK_BASE_URL: str = os.getenv('WEBHOOK_BASE_URL', 'https://hjlees.com')
    WEBSOCKET_BASE_URL: str = os.getenv('WEBSOCKET_BASE_URL', 'wss://hjlees.com/sambanova_todo/ws')
    
    # Redis Configuration (NEW)
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = safe_int(os.getenv('REDIS_PORT', '6379'), 6379)
    REDIS_PASSWORD: Optional[str] = os.getenv('REDIS_PASSWORD')
    REDIS_DB: int = safe_int(os.getenv('REDIS_DB', '0'), 0)
    
    # Composio Configuration (NEW)
    COMPOSIO_API_KEY: str = os.getenv('COMPOSIO_API_KEY', 'ak_68Xsj6WGv3Zl4ooBgkcD')
    COMPOSIO_PROJECT_ID: str = os.getenv('COMPOSIO_PROJECT_ID', 'pr_bz7nkY2wflSi')
    
    # Google Calendar Configuration
    GOOGLE_OAUTH2_TOKEN_B64: str = os.getenv('GOOGLE_OAUTH2_TOKEN_B64', '')
    
    # FusionPBX Configuration
    FREEPBX_DOMAIN: str = os.getenv('FREEPBX_DOMAIN', '136.113.215.142')
    FREEPBX_SIP_USERNAME: Optional[str] = os.getenv('FREEPBX_SIP_USERNAME')
    FREEPBX_SIP_PASSWORD: Optional[str] = os.getenv('FREEPBX_SIP_PASSWORD')
    TRANSFER_TIMEOUT: int = safe_int(os.getenv('TRANSFER_TIMEOUT', '30'), 30)
    SUPPORT_EXTENSION: str = os.getenv('SUPPORT_EXTENSION', '2000')
    SALES_EXTENSION: str = os.getenv('SALES_EXTENSION', '2000')
    GENERAL_EXTENSION: str = os.getenv('GENERAL_EXTENSION', '2000')
    OPERATOR_EXTENSION: str = os.getenv('OPERATOR_EXTENSION', '2000')
    
    # Sentry Configuration
    SENTRY_DSN: Optional[str] = os.getenv('SENTRY_DSN')
    
    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL: str = os.getenv('RATELIMIT_STORAGE_URL', 'redis://localhost:6379/1')
    RATELIMIT_DEFAULT: str = os.getenv('RATELIMIT_DEFAULT', '10 per minute')
    
    @classmethod
    def get_redis_url(cls) -> str:
        """Get Redis URL for connection"""
        if cls.REDIS_PASSWORD:
            return f"redis://:{cls.REDIS_PASSWORD}@{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
        else:
            return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
    
    @classmethod
    def validate_required_vars(cls) -> list:
        """Validate required environment variables"""
        required_vars = [
            'OPENAI_API_KEY',
            'DB_URI',
            'FLASK_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        return missing_vars
    
    @classmethod
    def get_redis_config(cls) -> dict:
        """Get Redis configuration dictionary"""
        return {
            'host': cls.REDIS_HOST,
            'port': cls.REDIS_PORT,
            'password': cls.REDIS_PASSWORD,
            'db': cls.REDIS_DB
        }
    
    @classmethod
    def get_composio_config(cls) -> dict:
        """Get Composio configuration dictionary"""
        return {
            'api_key': cls.COMPOSIO_API_KEY,
            'project_id': cls.COMPOSIO_PROJECT_ID
        }
    
    @classmethod
    def print_config_summary(cls):
        """Print configuration summary for debugging"""
        print("🔧 Sambanova Environment Configuration Summary")
        print("=" * 50)
        
        # Database
        print(f"📊 Database: {cls.DB_URI[:20]}..." if len(cls.DB_URI) > 20 else f"📊 Database: {cls.DB_URI}")
        
        # Redis
        redis_status = "✅ Configured" if cls.REDIS_HOST != 'localhost' else "⚠️ Using localhost"
        print(f"🔴 Redis: {cls.REDIS_HOST}:{cls.REDIS_PORT} ({redis_status})")
        
        # Composio
        composio_status = "✅ Configured" if cls.COMPOSIO_API_KEY else "❌ Not configured"
        print(f"🔗 Composio: {composio_status}")
        
        # OpenAI
        openai_status = "✅ Configured" if cls.OPENAI_API_KEY else "❌ Not configured"
        print(f"🤖 OpenAI: {openai_status}")
        
        # Twilio
        twilio_status = "✅ Configured" if cls.TWILIO_ACCOUNT_SID else "❌ Not configured"
        print(f"📞 Twilio: {twilio_status}")
        
        # Check for missing required variables
        missing = cls.validate_required_vars()
        if missing:
            print(f"❌ Missing required variables: {', '.join(missing)}")
        else:
            print("✅ All required variables configured")
        
        print("=" * 50)

# Global config instance
config = EnvironmentConfig()
