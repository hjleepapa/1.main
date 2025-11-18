#!/bin/bash

# Setup script for Convonet GitHub Repository
# This script prepares the convonet project files and pushes them to GitHub

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO_NAME="convonet"
GITHUB_USER="hjleepapa"
GITHUB_URL="git@github.com:${GITHUB_USER}/${REPO_NAME}.git"
PROJECT_ROOT="/Users/hj/Web Development Projects/1. Main"
REPO_DIR="${PROJECT_ROOT}/${REPO_NAME}_repo"
TEMP_DIR="${PROJECT_ROOT}/${REPO_NAME}_temp"

echo -e "${BLUE}🚀 Setting up Convonet GitHub Repository${NC}\n"

# Step 1: Clean up any existing temp/repo directories
echo -e "${YELLOW}🧹 Cleaning up existing directories...${NC}"
if [ -d "$REPO_DIR" ]; then
    rm -rf "$REPO_DIR"
fi
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# Step 2: Create temporary directory for staging
echo -e "${YELLOW}📁 Creating temporary staging directory...${NC}"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

# Step 3: Initialize git repository
echo -e "${YELLOW}🔧 Initializing git repository...${NC}"
git init
git branch -M main

# Step 4: Copy convonet module (excluding .git if it exists)
echo -e "${YELLOW}📦 Copying convonet module...${NC}"
rsync -av --exclude='.git' --exclude='__pycache__' "${PROJECT_ROOT}/convonet/" ./convonet/

# Step 5: Copy related root files
echo -e "${YELLOW}📦 Copying related root files...${NC}"
cp "${PROJECT_ROOT}/deepgram_service.py" ./
cp "${PROJECT_ROOT}/deepgram_webrtc_integration.py" ./
cp "${PROJECT_ROOT}/extensions.py" ./

# Step 6: Copy shared utilities
echo -e "${YELLOW}📦 Copying shared utilities...${NC}"
rsync -av --exclude='__pycache__' "${PROJECT_ROOT}/shared/" ./shared/

# Step 7: Copy relevant templates
echo -e "${YELLOW}📦 Copying templates...${NC}"
mkdir -p templates
cp "${PROJECT_ROOT}/templates/convonet_tech_spec.html" ./templates/
cp "${PROJECT_ROOT}/templates/convonet_system_architecture.html" ./templates/
cp "${PROJECT_ROOT}/templates/convonet_sequence_diagram.html" ./templates/
cp "${PROJECT_ROOT}/templates/base.html" ./templates/ 2>/dev/null || echo "Note: base.html may not exist"

# Step 8: Copy static assets
echo -e "${YELLOW}📦 Copying static assets...${NC}"
mkdir -p static
if [ -d "${PROJECT_ROOT}/static/convonet" ]; then
    rsync -av "${PROJECT_ROOT}/static/convonet/" ./static/convonet/
fi

# Step 9: Copy configuration files
echo -e "${YELLOW}📦 Copying configuration files...${NC}"
cp "${PROJECT_ROOT}/requirements.txt" ./
cp "${PROJECT_ROOT}/requirements_memory_optimized.txt" ./ 2>/dev/null || echo "Note: requirements_memory_optimized.txt may not exist"
cp "${PROJECT_ROOT}/Procfile" ./
cp "${PROJECT_ROOT}/render.yaml" ./
cp "${PROJECT_ROOT}/render_memory_optimized.yaml" ./ 2>/dev/null || echo "Note: render_memory_optimized.yaml may not exist"
cp "${PROJECT_ROOT}/render-build.sh" ./ 2>/dev/null || echo "Note: render-build.sh may not exist"
cp "${PROJECT_ROOT}/runtime.txt" ./ 2>/dev/null || echo "Note: runtime.txt may not exist"

# Step 10: Copy deployment scripts
echo -e "${YELLOW}📦 Copying deployment files...${NC}"
cp "${PROJECT_ROOT}/app.py" ./
cp "${PROJECT_ROOT}/app_memory_optimized.py" ./ 2>/dev/null || echo "Note: app_memory_optimized.py may not exist"
cp "${PROJECT_ROOT}/passenger_wsgi.py" ./
cp "${PROJECT_ROOT}/passenger_wsgi_memory_optimized.py" ./ 2>/dev/null || echo "Note: passenger_wsgi_memory_optimized.py may not exist"
cp "${PROJECT_ROOT}/deploy_memory_optimized.sh" ./ 2>/dev/null || echo "Note: deploy_memory_optimized.sh may not exist"
cp "${PROJECT_ROOT}/deploy_convonet_asgi.sh" ./ 2>/dev/null || echo "Note: deploy_convonet_asgi.sh may not exist"

# Step 11: Copy documentation
echo -e "${YELLOW}📦 Copying documentation...${NC}"
cp "${PROJECT_ROOT}/CONVONET_DEPLOYMENT_CONFIG.md" ./
cp "${PROJECT_ROOT}/WEBRTC_CALL_FLOW_DIAGRAM.md" ./
cp "${PROJECT_ROOT}/PRODUCTION_WEBSOCKET_SETUP.md" ./
if [ -f "${PROJECT_ROOT}/convonet/README_convonet.md" ]; then
    cp "${PROJECT_ROOT}/convonet/README_convonet.md" ./README.md
fi

# Step 12: Create .gitignore
echo -e "${YELLOW}📝 Creating .gitignore...${NC}"
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment variables
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Sensitive files
token.pickle
*.pem
*.key

# Audio recordings
recordings/
*.wav
*.mp3
*.m4a
!convonet/static/assets/img/*.wav

# Instance folder
instance/

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover

# Migrations (optional - uncomment if you don't want to track migrations)
# migrations/versions/*.py

# Archive
archive/
EOF

# Step 13: Create or update README.md
echo -e "${YELLOW}📝 Creating README.md...${NC}"
if [ ! -f "README.md" ] || [ -s "README.md" == 0 ]; then
cat > README.md << 'EOF'
# Convonet Voice AI Productivity System

Enterprise-grade voice AI platform combining LangGraph, Twilio, MCP, Team Management, Call Transfer, Sentry Monitoring, Redis, Composio, Audio Stream Player, and WebRTC Voice Integration.

## 🚀 Features

- **Voice AI Assistant**: WebRTC-based voice assistant with Deepgram STT and OpenAI TTS
- **Team Collaboration**: Multi-tenant team management with role-based access control
- **Call Transfer**: Seamless AI-to-human agent transfer via Twilio and FusionPBX
- **MCP Integration**: 38 tools for database operations, calendar, and external platforms
- **Redis Management**: Session and audio buffer management for real-time processing
- **Monitoring**: Comprehensive error tracking with Sentry
- **Composio Tools**: Integration with Slack, GitHub, Gmail, Notion, and Jira

## 📋 Requirements

- Python 3.9+
- PostgreSQL
- Redis
- OpenAI API Key
- Twilio Account
- Deepgram API Key
- FusionPBX (for call transfer)

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/hjleepapa/convonet.git
cd convonet
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (see `.env.example`)

4. Run database migrations:
```bash
flask db upgrade
```

5. Start the server:
```bash
python app.py
```

## 📚 Documentation

- [Technical Specification](templates/convonet_tech_spec.html)
- [System Architecture](templates/convonet_system_architecture.html)
- [Sequence Diagram](templates/convonet_sequence_diagram.html)
- [Deployment Guide](CONVONET_DEPLOYMENT_CONFIG.md)
- [WebRTC Call Flow](WEBRTC_CALL_FLOW_DIAGRAM.md)

## 🏗️ Architecture

See the [Technical Specification](templates/convonet_tech_spec.html) for detailed architecture documentation.

## 📄 License

MIT License

## 👤 Author

**HJ Lee**

- GitHub: [@hjleepapa](https://github.com/hjleepapa)

## 🙏 Acknowledgments

- LangGraph for AI orchestration
- Twilio for voice API
- OpenAI for LLM and TTS
- Deepgram for speech-to-text
- FusionPBX for call center integration
EOF
fi

# Step 14: Add remote repository
echo -e "${YELLOW}🔗 Adding remote repository...${NC}"
git remote add origin "$GITHUB_URL" 2>/dev/null || git remote set-url origin "$GITHUB_URL"

# Step 15: Add all files
echo -e "${YELLOW}📤 Adding files to git...${NC}"
git add .

# Step 16: Create initial commit
echo -e "${YELLOW}💾 Creating initial commit...${NC}"
git commit -m "Initial commit: Convonet Voice AI Productivity System

- WebRTC voice assistant with Deepgram STT and OpenAI TTS
- LangGraph AI orchestration with 38 MCP tools
- Team collaboration with role-based access control
- Call transfer to FusionPBX via Twilio
- Redis session and audio buffer management
- Composio integration for external platforms
- Comprehensive Sentry monitoring
- Production-ready deployment configuration"

# Step 17: Move to final location
echo -e "${YELLOW}📁 Moving to final repository location...${NC}"
cd "$PROJECT_ROOT"
mv "$TEMP_DIR" "$REPO_DIR"

# Step 18: Push to GitHub
echo -e "${YELLOW}🚀 Pushing to GitHub...${NC}"
cd "$REPO_DIR"
echo -e "${GREEN}Ready to push!${NC}"
echo -e "${BLUE}Repository location: ${REPO_DIR}${NC}"
echo -e "\n${YELLOW}Run the following commands to push:${NC}"
echo -e "${GREEN}cd ${REPO_DIR}${NC}"
echo -e "${GREEN}git push -u origin main${NC}"
echo -e "\n${BLUE}Pushing now... (this will ask for GitHub credentials if needed)${NC}"
if git push -u origin main; then
    echo -e "\n${GREEN}✅ Successfully pushed to GitHub!${NC}"
    echo -e "${BLUE}Repository URL: https://github.com/${GITHUB_USER}/${REPO_NAME}${NC}"
else
    echo -e "\n${YELLOW}⚠️  Push failed. You may need to authenticate or run manually:${NC}"
    echo -e "${GREEN}cd ${REPO_DIR}${NC}"
    echo -e "${GREEN}git push -u origin main${NC}"
fi

echo -e "\n${GREEN}✅ Repository setup complete!${NC}"
echo -e "${BLUE}Repository location: ${REPO_DIR}${NC}"

