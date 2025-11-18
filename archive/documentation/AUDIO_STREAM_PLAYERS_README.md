# Audio Stream Players for Convonet Project

Two audio stream player applications for viewing, analyzing, and playing audio streams from Redis audio buffers.

## 🎵 Applications Overview

### 1. Full Audio Player (`audio_stream_player.py`)
**Features**: Complete audio playback with PyAudio integration
- ✅ Real-time audio playback
- ✅ Multiple audio format support
- ✅ PyAudio integration for high-quality audio
- ✅ Real-time controls (play/stop)
- ✅ Session management

**Requirements**: PyAudio, PortAudio
**Port**: 5001
**URL**: http://localhost:5001

### 2. Simple Audio Player (`simple_audio_player.py`)
**Features**: Audio analysis and download without PyAudio dependency
- ✅ Audio buffer analysis and inspection
- ✅ WAV file creation and download
- ✅ Format detection and validation
- ✅ No PyAudio dependency (easier installation)
- ✅ Comprehensive audio data analysis

**Requirements**: Flask, Redis (optional)
**Port**: 5002
**URL**: http://localhost:5002

## 🚀 Quick Start

### Option 1: Simple Audio Player (Recommended)
```bash
# Install dependencies
pip install flask flask-socketio redis

# Start the simple audio player
python simple_audio_player.py

# Visit http://localhost:5002
```

### Option 2: Full Audio Player (with PyAudio)
```bash
# Install PortAudio (macOS)
brew install portaudio

# Install dependencies
pip install -r requirements_audio_player.txt

# Start the full audio player
python start_audio_player.py

# Visit http://localhost:5001
```

## 📊 Features Comparison

| Feature | Simple Player | Full Player |
|---------|---------------|-------------|
| View Sessions | ✅ | ✅ |
| Audio Analysis | ✅ | ✅ |
| Download Audio | ✅ | ✅ |
| Play Audio | ❌ | ✅ |
| Real-time Controls | ❌ | ✅ |
| PyAudio Required | ❌ | ✅ |
| Easy Installation | ✅ | ❌ |

## 🔧 Installation Guide

### Simple Audio Player (No PyAudio)

```bash
# 1. Install basic dependencies
pip install flask flask-socketio redis

# 2. Test the installation
python test_simple_audio_player.py

# 3. Start the player
python simple_audio_player.py

# 4. Open browser
open http://localhost:5002
```

### Full Audio Player (With PyAudio)

#### macOS Installation:
```bash
# 1. Install PortAudio
brew install portaudio

# 2. Install Python dependencies
pip install -r requirements_audio_player.txt

# 3. Test the installation
python test_audio_player.py

# 4. Start the player
python start_audio_player.py

# 5. Open browser
open http://localhost:5001
```

#### Ubuntu/Debian Installation:
```bash
# 1. Install PortAudio
sudo apt-get install portaudio19-dev python3-pyaudio

# 2. Install Python dependencies
pip install -r requirements_audio_player.txt

# 3. Start the player
python start_audio_player.py
```

## 🎯 Usage Guide

### Simple Audio Player Features

#### 1. Session Management
- **View Active Sessions**: See all WebRTC sessions with audio buffers
- **Session Information**: User details, authentication status, recording status
- **Real-time Updates**: Live session status updates

#### 2. Audio Analysis
- **Buffer Inspection**: View audio buffer length and content
- **Format Detection**: Automatic detection of audio formats (WAV, MP3, OGG, WebM, etc.)
- **Data Validation**: Base64 validation and corruption detection
- **Hex Analysis**: View raw audio data in hexadecimal format

#### 3. Audio Download
- **WAV Creation**: Convert raw audio to proper WAV format
- **Multiple Formats**: Try different audio parameters automatically
- **File Download**: Download audio as WAV files for analysis

### Full Audio Player Features

#### 1. Real-time Audio Playback
- **Live Playback**: Play audio streams directly from Redis
- **Audio Controls**: Start/stop playback with real-time feedback
- **Format Support**: Multiple audio format detection and conversion

#### 2. Advanced Audio Processing
- **PyAudio Integration**: High-quality audio processing
- **Real-time Controls**: Live play/stop controls
- **Audio Quality**: Professional audio playback

## 🔍 Audio Analysis Features

### Buffer Analysis
```json
{
  "base64_length": 137894,
  "decoded_length": 137894,
  "first_20_bytes_hex": "8c81003c80fb03fffefffefffe1f43b67501ffff",
  "null_bytes_count": 0,
  "null_bytes_percentage": 0.0,
  "unique_bytes": 256,
  "has_repetitive_pattern": false,
  "detected_format": "Unknown"
}
```

### Format Detection
- **RIFF/WAV**: `RIFF` header with `WAVE` format
- **MP3**: `ID3` tags or sync headers
- **OGG**: `OggS` header
- **WebM**: Matroska container format
- **MP4/M4A**: `ftyp` header

### Corruption Detection
- **Null Bytes**: Detect excessive null bytes (>80%)
- **Repetitive Patterns**: Identify corrupted or repetitive data
- **Base64 Validation**: Verify base64 encoding integrity

## 🛠️ API Endpoints

### Simple Audio Player (Port 5002)

```bash
# Get active sessions
GET /api/sessions

# Get session details
GET /api/session/{session_id}/info

# Analyze audio buffer
GET /api/session/{session_id}/analyze

# Download audio as WAV
GET /api/session/{session_id}/download
```

### Full Audio Player (Port 5001)

```bash
# Get active sessions
GET /api/sessions

# Get session details
GET /api/session/{session_id}/info

# Start audio playback
POST /api/session/{session_id}/play

# Stop audio playback
POST /api/session/{session_id}/stop

# Download audio as WAV
GET /api/session/{session_id}/download
```

## 🐛 Troubleshooting

### Common Issues

#### 1. PyAudio Installation Issues
```bash
# macOS
brew install portaudio
pip install pyaudio

# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio

# Windows
pip install pyaudio
```

#### 2. Redis Connection Issues
```bash
# Check Redis status
redis-cli ping

# Check environment variables
echo $REDIS_HOST
echo $REDIS_PORT
echo $REDIS_PASSWORD
```

#### 3. Audio Format Issues
- Use the **Simple Audio Player** for format analysis
- Check the **Audio Analysis** feature for detailed format information
- Try different audio parameters automatically

### Debug Commands

```bash
# Test simple audio player
python test_simple_audio_player.py

# Test full audio player
python test_audio_player.py

# Check Redis connection
python -c "from convonet.redis_manager import redis_manager; print('Redis available:', redis_manager.is_available())"
```

## 📈 Performance Tips

### Simple Audio Player
- **Memory Efficient**: No PyAudio dependency
- **Fast Analysis**: Quick audio buffer inspection
- **Easy Deployment**: Minimal dependencies

### Full Audio Player
- **High Quality**: Professional audio playback
- **Real-time**: Live audio streaming
- **Advanced Features**: Complete audio processing

## 🔒 Security Considerations

- **Session Access**: Only authenticated sessions are accessible
- **Audio Privacy**: Audio data is not stored permanently
- **Network Security**: Use HTTPS in production
- **Access Control**: Implement authentication for production use

## 🚀 Deployment

### Development
```bash
# Simple player (recommended for development)
python simple_audio_player.py

# Full player (for production with audio playback)
python start_audio_player.py
```

### Production
```bash
# Use Gunicorn for production
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5002 simple_audio_player:app

# Or use the full player
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5001 audio_stream_player:app
```

## 📚 Additional Resources

- **Redis Data Guide**: `REDIS_DATA_GUIDE.md`
- **Audio Player README**: `AUDIO_PLAYER_README.md`
- **Redis Explorer**: `redis_data_explorer.py`

## 🎯 Use Cases

### Debugging WebRTC Audio Issues
1. **Use Simple Player** to analyze audio buffers
2. **Check format detection** and corruption
3. **Download audio files** for external analysis
4. **Monitor session data** in real-time

### Testing Audio Quality
1. **Use Full Player** for audio playback
2. **Test different formats** automatically
3. **Verify audio quality** with real playback
4. **Debug audio processing** issues

### Production Monitoring
1. **Monitor active sessions** and audio buffers
2. **Track audio format** compatibility
3. **Analyze audio data** for quality issues
4. **Debug Redis** audio storage

## 🎉 Conclusion

Both audio stream players provide comprehensive tools for working with Redis audio buffers:

- **Simple Player**: Perfect for analysis, debugging, and easy deployment
- **Full Player**: Complete audio playback with professional features

Choose the **Simple Player** for most use cases, and the **Full Player** when you need real-time audio playback capabilities.
