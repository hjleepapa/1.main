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

- [Technical Specification](docs/convonet_tech_spec.md)
- [System Architecture](docs/convonet_system_architecture.md)
- [Sequence Diagram](docs/convonet_sequence_diagram.md)
- [Deployment Guide](CONVONET_DEPLOYMENT_CONFIG.md)
- [WebRTC Call Flow](WEBRTC_CALL_FLOW_DIAGRAM.md)

## 🏗️ Architecture

See the [Technical Specification](docs/convonet_tech_spec.md) for detailed architecture documentation.

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
