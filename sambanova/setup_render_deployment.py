#!/usr/bin/env python3
"""
Render.com Deployment Setup Script
Helps configure environment variables for Render deployment
"""

import os
import sys
from pathlib import Path

def print_render_setup_instructions():
    """Print instructions for setting up Render environment variables"""
    print("🚀 Render.com Environment Variables Setup")
    print("=" * 60)
    print()
    print("📋 REQUIRED ENVIRONMENT VARIABLES FOR RENDER")
    print("=" * 60)
    print()
    
    # Database
    print("🗄️ DATABASE CONFIGURATION")
    print("-" * 30)
    print("DB_URI=postgresql://username:password@host:port/database_name")
    print("(Use your Render PostgreSQL database URL)")
    print()
    
    # Flask
    print("🔐 FLASK CONFIGURATION")
    print("-" * 30)
    print("FLASK_KEY=your-secret-key-here")
    print("(Generate a strong random string)")
    print()
    
    # OpenAI
    print("🤖 OPENAI CONFIGURATION")
    print("-" * 30)
    print("OPENAI_API_KEY=sk-your-openai-api-key")
    print("(Your OpenAI API key)")
    print()
    
    # Twilio
    print("📞 TWILIO CONFIGURATION")
    print("-" * 30)
    print("TWILIO_ACCOUNT_SID=your-twilio-account-sid")
    print("TWILIO_AUTH_TOKEN=your-twilio-auth-token")
    print("TWILIO_PHONE_NUMBER=your-twilio-phone-number")
    print()
    
    # Webhooks
    print("🌐 WEBHOOK CONFIGURATION")
    print("-" * 30)
    print("WEBHOOK_BASE_URL=https://your-app-name.onrender.com")
    print("WEBSOCKET_BASE_URL=wss://your-app-name.onrender.com/sambanova_todo/ws")
    print("(Replace 'your-app-name' with your actual Render app name)")
    print()
    
    # Redis
    print("🔴 REDIS CONFIGURATION (NEW)")
    print("-" * 30)
    print("REDIS_HOST=your-redis-host")
    print("REDIS_PORT=6379")
    print("REDIS_PASSWORD=your-redis-password")
    print("REDIS_DB=0")
    print("(Your Redis database credentials)")
    print()
    
    # Composio
    print("🔗 COMPOSIO CONFIGURATION (NEW)")
    print("-" * 30)
    print("COMPOSIO_API_KEY=ak_68Xsj6WGv3Zl4ooBgkcD")
    print("COMPOSIO_PROJECT_ID=pr_bz7nkY2wflSi")
    print("(Your Composio credentials)")
    print()
    
    # Google Calendar
    print("📅 GOOGLE CALENDAR CONFIGURATION")
    print("-" * 30)
    print("GOOGLE_OAUTH2_TOKEN_B64=your-base64-encoded-oauth2-token")
    print()
    
    # FreePBX
    print("📞 FREEPBX CONFIGURATION")
    print("-" * 30)
    print("FREEPBX_DOMAIN=34.26.59.14")
    print("TRANSFER_TIMEOUT=30")
    print("SUPPORT_EXTENSION=2000")
    print("SALES_EXTENSION=2000")
    print("GENERAL_EXTENSION=2000")
    print("OPERATOR_EXTENSION=2000")
    print()
    
    # Rate Limiting
    print("🚦 RATE LIMITING CONFIGURATION (NEW)")
    print("-" * 30)
    print("RATELIMIT_STORAGE_URL=redis://user:pass@host:port/db")
    print("RATELIMIT_DEFAULT=10 per minute")
    print()
    
    # Sentry
    print("📊 SENTRY CONFIGURATION (OPTIONAL)")
    print("-" * 30)
    print("SENTRY_DSN=your-sentry-dsn-here")
    print()

def print_render_dashboard_instructions():
    """Print instructions for adding variables in Render dashboard"""
    print("🔧 HOW TO ADD ENVIRONMENT VARIABLES IN RENDER")
    print("=" * 60)
    print()
    print("Method 1: Render Dashboard")
    print("-" * 30)
    print("1. Go to your Render dashboard")
    print("2. Select your Sambanova app")
    print("3. Go to 'Environment' tab")
    print("4. Click 'Add Environment Variable'")
    print("5. Add each variable with its value")
    print("6. Click 'Save Changes'")
    print()
    print("Method 2: Render CLI")
    print("-" * 30)
    print("1. Install Render CLI: npm install -g @render/cli")
    print("2. Login: render login")
    print("3. Set variables:")
    print("   render env set DB_URI=postgresql://user:pass@host:port/db")
    print("   render env set OPENAI_API_KEY=sk-your-openai-key")
    print("   render env set REDIS_HOST=your-redis-host")
    print("   # ... add all variables")
    print()

def print_deployment_checklist():
    """Print deployment checklist"""
    print("🚀 DEPLOYMENT CHECKLIST")
    print("=" * 60)
    print()
    print("Before Deployment:")
    print("-" * 20)
    print("□ All environment variables added to Render")
    print("□ Redis database configured")
    print("□ Composio API key set")
    print("□ Twilio credentials configured")
    print("□ Webhook URLs updated for Render")
    print()
    print("After Deployment:")
    print("-" * 20)
    print("□ Check logs for Redis connection")
    print("□ Check logs for Composio connection")
    print("□ Test voice commands")
    print("□ Test external integrations")
    print("□ Monitor performance")
    print()

def print_demo_script():
    """Print demo script for Hackathon"""
    print("🎯 HACKATHON DEMO SCRIPT")
    print("=" * 60)
    print()
    print("Perfect Demo Script:")
    print("-" * 20)
    print("1. Show Environment Variables in Render dashboard")
    print("2. Show Redis Integration: Session persistence across restarts")
    print("3. Show Composio Tools: 50+ external integrations")
    print("4. Show Voice Commands: Multi-step workflows")
    print("5. Show Real-time Features: Team notifications")
    print()
    print("Demo Flow:")
    print("-" * 10)
    print("Call your Twilio number and say:")
    print('"Create a todo for reviewing Redis integration"')
    print('"Assign it to John in the dev team"')
    print('"Send a Slack message to dev-team channel"')
    print('"Create a GitHub issue for Redis implementation"')
    print('"Show me my todos"')
    print()

def main():
    """Main setup function"""
    print_render_setup_instructions()
    print()
    print_render_dashboard_instructions()
    print()
    print_deployment_checklist()
    print()
    print_demo_script()
    
    print("🎉 Your Sambanova project is ready for Render.com deployment!")
    print("📖 See RENDER_ENVIRONMENT_SETUP.md for detailed instructions")
    print("🚀 Perfect for Hackathon success! 🏆")

if __name__ == "__main__":
    main()
