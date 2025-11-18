# Audio Stream Player

A web application to play audio streams from Redis audio buffers stored in the Convonet project.

## Features

- 🎵 **Play Audio Streams**: Play audio from Redis audio buffers
- 📊 **Session Management**: View and manage active WebRTC sessions
- 🔍 **Audio Analysis**: Analyze audio buffer data and format
- 💾 **Download Audio**: Download audio as WAV files
- 🎛️ **Real-time Controls**: Start/stop playback with real-time feedback
- 📱 **Web Interface**: Modern, responsive web interface

## Installation

### 1. Install Dependencies

```bash
# Install required packages
pip install -r requirements_audio_player.txt

# For PyAudio on macOS (if needed)
brew install portaudio
pip install pyaudio

# For PyAudio on Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### 2. Verify Redis Connection

Make sure your Redis server is running and accessible:

```bash
# Check Redis connection
python -c "from convonet.redis_manager import redis_manager; print('Redis available:', redis_manager.is_available())"
```

## Usage

### 1. Start the Audio Player

```bash
# Method 1: Using the startup script
python start_audio_player.py

# Method 2: Direct execution
python audio_stream_player.py
```

### 2. Access the Web Interface

Open your browser and go to:
```
http://localhost:5001
```

### 3. Using the Interface

1. **View Sessions**: The interface shows all active WebRTC sessions
2. **Session Info**: Click "ℹ️ Info" to see detailed session data
3. **Play Audio**: Click "▶️ Play" to play audio from a session
4. **Stop Audio**: Click "⏹️ Stop" to stop playback
5. **Download**: Click "💾 Download" to download audio as WAV file

## API Endpoints

### Sessions
- `GET /api/sessions` - Get list of active sessions
- `GET /api/session/{session_id}/info` - Get detailed session information

### Audio Playback
- `POST /api/session/{session_id}/play` - Start audio playback
- `POST /api/session/{session_id}/stop` - Stop audio playback
- `GET /api/session/{session_id}/download` - Download audio as WAV file

## Audio Format Support

The player automatically handles different audio formats:

- **Raw PCM**: Automatically detects and converts to WAV
- **Multiple Parameters**: Tries different audio parameters:
  - 16-bit, 44.1kHz, mono
  - 16-bit, 16kHz, mono  
  - 8-bit, 44.1kHz, mono
  - 16-bit, 44.1kHz, stereo

## Troubleshooting

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

#### 3. Audio Playback Issues
- Check if audio device is available
- Verify audio buffer contains valid data
- Check audio format compatibility

### Debug Mode

Run with debug logging:
```bash
export FLASK_DEBUG=1
python audio_stream_player.py
```

## Architecture

### Components

1. **Flask Web Server**: Handles HTTP requests and serves the web interface
2. **Socket.IO**: Real-time communication for playback status
3. **Redis Integration**: Reads audio buffers from Redis sessions
4. **PyAudio**: Audio playback and format conversion
5. **Web Interface**: Modern, responsive UI for session management

### Data Flow

1. **Session Detection**: Scans Redis for active WebRTC sessions
2. **Audio Loading**: Retrieves base64-encoded audio buffers from Redis
3. **Format Conversion**: Converts raw audio data to WAV format
4. **Playback**: Uses PyAudio to play audio streams
5. **Real-time Updates**: Socket.IO provides live playback status

## Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password
REDIS_DB=0

# Audio Configuration
AUDIO_CHUNK_SIZE=1024
AUDIO_FORMAT=pyaudio.paInt16
AUDIO_CHANNELS=1
AUDIO_RATE=44100
```

### Customization

You can modify the audio player behavior by editing:

- **Audio Parameters**: Change sample rate, channels, format in `audio_stream_player.py`
- **UI Styling**: Modify CSS in `templates/audio_player.html`
- **API Endpoints**: Add new endpoints in `audio_stream_player.py`

## Security Considerations

- **Session Access**: Only authenticated sessions are accessible
- **Audio Privacy**: Audio data is not stored permanently
- **Network Security**: Use HTTPS in production
- **Access Control**: Implement authentication for production use

## Performance

### Optimization Tips

1. **Audio Buffer Size**: Adjust chunk size for better performance
2. **Redis Connection**: Use connection pooling for better Redis performance
3. **Memory Management**: Clean up temporary files after playback
4. **Concurrent Playback**: Limit simultaneous audio streams

### Monitoring

- **Redis Memory**: Monitor Redis memory usage for audio buffers
- **Audio Quality**: Check audio format and sample rate
- **Playback Latency**: Monitor audio processing delays

## Development

### Adding Features

1. **New Audio Formats**: Add format detection in `AudioStreamPlayer` class
2. **Enhanced UI**: Modify `templates/audio_player.html`
3. **API Endpoints**: Add new routes in `audio_stream_player.py`
4. **Real-time Features**: Use Socket.IO for live updates

### Testing

```bash
# Test Redis connection
python -c "from convonet.redis_manager import redis_manager; print(redis_manager.is_available())"

# Test audio playback
python -c "import pyaudio; print('PyAudio available')"

# Test Flask app
python audio_stream_player.py
```

## License

This project is part of the Convonet Hackathon project.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Verify Redis and audio dependencies
3. Check the debug logs
4. Review the API documentation
