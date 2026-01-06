# WebRTC ASR and TTS Components

## Overview

This document details the ASR (Automatic Speech Recognition) and TTS (Text-to-Speech) components used in the WebRTC voice assistant.

---

## ASR (Speech-to-Text): Deepgram

### Component Details

**Service:** Deepgram  
**Model:** Nova-2 (latest model)  
**Integration File:** `convonet/deepgram_webrtc_integration.py`  
**Service File:** `convonet/deepgram_service.py`

### Implementation

```python
# From convonet/webrtc_voice_server.py
from deepgram_webrtc_integration import transcribe_audio_with_deepgram_webrtc

# Usage in audio processing
transcribed_text = transcribe_audio_with_deepgram_webrtc(audio_buffer, language="en")
```

### Why Deepgram?

**Advantages:**
- ✅ **Real-time streaming optimized** - Designed for WebRTC chunks
- ✅ **Low latency** - 200-500ms response time
- ✅ **High accuracy** - 95%+ accuracy with Nova-2 model
- ✅ **WebRTC native** - Handles small audio buffers effectively
- ✅ **Cost-effective** - $0.0043 per minute (Nova-2 model)
- ✅ **Production-ready** - Stable and reliable

**Technical Details:**
- Processes audio buffers directly from WebRTC
- Handles WebM/Opus audio format from browser
- Supports multiple languages
- Streaming-optimized architecture

### Configuration

**Environment Variable:**
```bash
DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

**API Endpoint:**
- Deepgram REST API
- Real-time streaming support available

### Code Location

**Main Integration:**
- `convonet/deepgram_webrtc_integration.py` - WebRTC-specific wrapper
- `convonet/deepgram_service.py` - Core Deepgram service

**Usage:**
- `convonet/webrtc_voice_server.py` (line 1288)

---

## TTS (Text-to-Speech): OpenAI TTS

### Component Details

**Service:** OpenAI Audio API  
**Model:** `tts-1`  
**Voice:** `nova` (default)  
**Format:** MP3

### Implementation

```python
# From convonet/webrtc_voice_server.py
from openai import OpenAI

openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Generate speech
speech_response = openai_client.audio.speech.create(
    model="tts-1",
    voice="nova",  # Options: alloy, echo, fable, onyx, nova, shimmer
    input=agent_response,
    response_format="mp3"
)

# Convert to base64 for transmission
audio_base64 = base64.b64encode(speech_response.content).decode('utf-8')
```

### Available Voices

OpenAI TTS provides 6 voice options:
- `alloy` - Neutral, balanced voice
- `echo` - Clear, professional voice
- `fable` - Warm, friendly voice
- `onyx` - Deep, authoritative voice
- `nova` - **Default** - Natural, conversational voice
- `shimmer` - Soft, gentle voice

### Why OpenAI TTS?

**Advantages:**
- ✅ **High quality** - Natural-sounding voices
- ✅ **Consistent** - Same voice across all responses
- ✅ **Fast generation** - Low latency
- ✅ **Multiple voices** - 6 voice options available
- ✅ **Cost-effective** - $15 per 1M characters (~$0.015 per 1000 characters)
- ✅ **Reliable** - Production-grade service

**Technical Details:**
- Generates MP3 audio format
- Base64 encoded for WebSocket transmission
- Played directly in browser via HTML5 Audio API
- Supports streaming (though current implementation uses full response)

### Configuration

**Environment Variable:**
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**API Endpoint:**
- OpenAI Audio API (`https://api.openai.com/v1/audio/speech`)

### Code Location

**Usage:**
- `convonet/webrtc_voice_server.py` (lines 1228, 1371, 1423)

---

## Complete Flow

### Audio Processing Pipeline

```
1. User speaks in browser
   ↓
2. MediaRecorder captures audio (WebM/Opus)
   ↓
3. Audio sent via WebSocket to server
   ↓
4. Server buffers audio in Redis
   ↓
5. ASR: Deepgram transcribes audio → text
   ↓
6. LangGraph processes text → generates response
   ↓
7. TTS: OpenAI converts response → MP3 audio
   ↓
8. Audio sent back via WebSocket (base64)
   ↓
9. Browser plays audio via HTML5 Audio API
```

### Code Flow

```python
# 1. Audio received
@socketio.on('stop_recording', namespace='/voice')
def handle_stop_recording(data):
    audio_buffer = base64.b64decode(data['audio'])
    
    # 2. Transcribe with Deepgram
    transcribed_text = transcribe_audio_with_deepgram_webrtc(audio_buffer, language="en")
    
    # 3. Process with LangGraph
    agent_response = asyncio.run(process_with_agent(transcribed_text, user_id, user_name))
    
    # 4. Generate speech with OpenAI TTS
    speech_response = openai_client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=agent_response,
        response_format="mp3"
    )
    
    # 5. Send to client
    audio_base64 = base64.b64encode(speech_response.content).decode('utf-8')
    emit('agent_response', {'audio': audio_base64})
```

---

## Cost Analysis

### Deepgram ASR
- **Model:** Nova-2
- **Cost:** $0.0043 per minute
- **Example:** 1000 minutes/month = $4.30/month

### OpenAI TTS
- **Model:** tts-1
- **Cost:** $15 per 1M characters (~$0.015 per 1000 characters)
- **Example:** Average response ~200 characters
- **1000 responses** = ~200,000 characters = ~$3.00/month

### Total Cost (Example)
- **1000 conversations/month** (avg 2 minutes each)
- ASR: 2000 minutes × $0.0043 = **$8.60**
- TTS: 2000 responses × 200 chars = 400,000 chars = **$6.00**
- **Total: ~$14.60/month**

---

## Alternatives Considered

### ASR Alternatives

**1. OpenAI Whisper**
- ✅ High accuracy
- ❌ Higher latency (not optimized for real-time)
- ❌ More expensive for real-time use
- ❌ Better for batch processing

**2. Google Cloud Speech-to-Text**
- ✅ Good accuracy
- ✅ Real-time streaming support
- ❌ More complex setup
- ❌ Higher cost ($0.006 per minute)

**3. AssemblyAI**
- ✅ Good accuracy
- ❌ Higher latency than Deepgram
- ❌ More expensive

**4. Web Speech API (Browser)**
- ✅ Free
- ✅ No server processing
- ❌ Browser-dependent quality
- ❌ Inconsistent across browsers
- ❌ Privacy concerns (sent to Google)

**Selected: Deepgram** - Best balance of accuracy, latency, and cost for WebRTC

### TTS Alternatives

**1. Google Cloud Text-to-Speech**
- ✅ High quality
- ✅ Multiple voices
- ❌ More expensive ($0.016 per 1000 characters)
- ❌ More complex setup

**2. Amazon Polly**
- ✅ Good quality
- ✅ Multiple voices
- ❌ More expensive
- ❌ AWS account required

**3. Azure Cognitive Services Speech**
- ✅ Good quality
- ❌ More expensive
- ❌ Azure account required

**4. Browser TTS (Web Speech API)**
- ✅ Free
- ✅ No server processing
- ❌ Browser-dependent quality
- ❌ Limited voice options
- ❌ Inconsistent across browsers

**Selected: OpenAI TTS** - Best balance of quality, cost, and simplicity

---

## Configuration Files

### Environment Variables Required

```bash
# Deepgram ASR
DEEPGRAM_API_KEY=your_deepgram_api_key

# OpenAI TTS
OPENAI_API_KEY=your_openai_api_key
```

### Dependencies

**requirements.txt:**
```txt
openai>=1.0.0
deepgram-sdk>=3.0.0  # If using Deepgram SDK
```

---

## Performance Metrics

### Deepgram ASR
- **Latency:** 200-500ms
- **Accuracy:** 95%+ (Nova-2 model)
- **Supported Languages:** 50+ languages
- **Audio Formats:** WebM, Opus, PCM, MP3, etc.

### OpenAI TTS
- **Latency:** 500-1000ms (for full response)
- **Quality:** High (natural-sounding)
- **Supported Languages:** 50+ languages
- **Audio Format:** MP3, Opus, AAC, FLAC

---

## Troubleshooting

### Deepgram Issues

**Problem:** "Deepgram service not available"
- **Solution:** Check `DEEPGRAM_API_KEY` environment variable
- **Solution:** Verify Deepgram API key is valid
- **Solution:** Check network connectivity to Deepgram API

**Problem:** Low transcription accuracy
- **Solution:** Ensure good audio quality (48kHz sample rate)
- **Solution:** Check microphone settings (noise suppression enabled)
- **Solution:** Verify language parameter matches user's language

### OpenAI TTS Issues

**Problem:** "OpenAI API error"
- **Solution:** Check `OPENAI_API_KEY` environment variable
- **Solution:** Verify API key has sufficient credits
- **Solution:** Check rate limits

**Problem:** Audio not playing in browser
- **Solution:** Verify base64 encoding is correct
- **Solution:** Check browser audio codec support (MP3)
- **Solution:** Ensure audio element is properly initialized

---

## Future Enhancements

### Potential Improvements

1. **Streaming TTS**
   - Currently: Full response generated, then sent
   - Future: Stream audio chunks as they're generated
   - Benefit: Lower perceived latency

2. **Multiple ASR Providers**
   - Fallback to OpenAI Whisper if Deepgram fails
   - A/B testing different providers
   - Cost optimization based on usage

3. **Voice Cloning**
   - Custom voice training
   - Brand-specific voices
   - Multi-language voice support

4. **Real-time Streaming ASR**
   - Currently: Process complete audio buffer
   - Future: Stream transcription as user speaks
   - Benefit: Faster response, better UX

---

## Summary

| Component | Service | Model | Cost | Latency | Quality |
|-----------|---------|-------|------|---------|---------|
| **ASR** | Deepgram | Nova-2 | $0.0043/min | 200-500ms | 95%+ |
| **TTS** | OpenAI | tts-1 | $15/1M chars | 500-1000ms | High |

**Key Advantages:**
- ✅ Real-time optimized for WebRTC
- ✅ High accuracy and quality
- ✅ Cost-effective
- ✅ Production-ready
- ✅ Easy to configure and maintain

