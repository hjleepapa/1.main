# Twilio Alternatives for Telephony Integration

## Current Twilio Usage

Based on your codebase, you're currently using Twilio for:

1. **Inbound Calls**: Receiving calls from phone numbers via Twilio webhooks
2. **Outbound Calls**: Making calls to agents (SIP) and users (PSTN) for transfers
3. **ASR/TTS**: Speech recognition and text-to-speech (via Twilio's services)
4. **Call Control**: TwiML for dynamic call flow control

## Alternative Solutions Using Your Existing Infrastructure

Since you already have **FusionPBX (FreeSWITCH)** infrastructure, here are alternatives:

---

## Option 1: Direct FusionPBX/FreeSWITCH Integration (Recommended)

### Overview
Use FusionPBX directly for all telephony, eliminating Twilio dependency entirely.

### Architecture

```
Phone Number (DID) → FusionPBX → Your Application
                    ↓
              FreeSWITCH ESL
                    ↓
         Python/Flask Application
```

### Implementation Steps

#### 1. **Inbound Calls via DID/Trunk**

**Setup:**
- Purchase DID (Direct Inward Dialing) from SIP provider (e.g., Flowroute, Telnyx, VoIP.ms)
- Configure trunk in FusionPBX pointing to your DID provider
- Create inbound route in FusionPBX that routes calls to your application

**FusionPBX Configuration:**
```xml
<!-- Inbound route: Calls to DID → Application -->
<extension name="voice_assistant_inbound">
  <condition field="destination_number" expression="^YOUR_DID_NUMBER$">
    <action application="answer"/>
    <action application="lua" data="voice_assistant.lua"/>
    <!-- Or use mod_http or mod_event_socket -->
  </condition>
</extension>
```

**Python Integration via FreeSWITCH ESL (Event Socket Library):**
```python
import freeswitchESL

def handle_inbound_call(call_uuid, caller_id, destination):
    """Handle inbound call via FreeSWITCH ESL"""
    # Connect to FreeSWITCH via ESL
    con = freeswitchESL.ESLconnection("127.0.0.1", "8021", "ClueCon")
    
    # Answer the call
    con.execute("answer", "", call_uuid)
    
    # Play greeting
    con.execute("playback", "ivr/ivr-welcome.wav", call_uuid)
    
    # Start recording audio
    con.execute("record_session", "/tmp/call_audio.wav", call_uuid)
    
    # Send audio to your ASR service
    # Process with your conversation engine
    # Generate TTS response
    # Play response back
    
    return True
```

#### 2. **Outbound Calls for Transfers**

**Instead of Twilio API:**
```python
# OLD (Twilio):
# client.calls.create(to=sip_target, from_=caller_id, url=conference_url)

# NEW (FreeSWITCH ESL):
import freeswitchESL

def initiate_agent_transfer(extension, user_number, session_data):
    """Initiate transfer using FreeSWITCH instead of Twilio"""
    con = freeswitchESL.ESLconnection("127.0.0.1", "8021", "ClueCon")
    
    # Create conference
    conference_name = f"transfer-{session_id}"
    con.execute("conference", f"{conference_name}@default", call_uuid)
    
    # Originate call to agent (SIP)
    agent_originate = f"originate {{{{origination_caller_id_number={caller_id}}}}} sofia/internal/{extension}@{freepbx_domain} &conference({conference_name}@default)"
    con.api(agent_originate)
    
    # Originate call to user (PSTN via trunk)
    user_originate = f"originate {{{{origination_caller_id_number={caller_id}}}}} sofia/gateway/your_trunk/{user_number} &conference({conference_name}@default)"
    con.api(user_originate)
    
    # Cache customer profile
    cache_call_center_profile(extension, session_data, call_id=call_uuid)
    
    return True
```

**FreeSWITCH Dialplan for Transfers:**
```xml
<extension name="agent_transfer">
  <condition field="destination_number" expression="^transfer_(\d+)$">
    <action application="answer"/>
    <action application="set" data="conference_name=transfer-${caller_id_number}"/>
    <action application="conference" data="${conference_name}@default"/>
  </condition>
</extension>
```

#### 3. **ASR/TTS Integration**

**Option A: Google Cloud Speech-to-Text & Text-to-Speech**
```python
from google.cloud import speech, texttospeech

# ASR
def transcribe_audio(audio_file):
    client = speech.SpeechClient()
    with open(audio_file, "rb") as audio_file:
        content = audio_file.read()
    
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=8000,
        language_code="en-US",
    )
    
    response = client.recognize(config=config, audio=audio)
    return response.results[0].alternatives[0].transcript

# TTS
def synthesize_speech(text):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    # Save to file for FreeSWITCH to play
    with open("/tmp/tts_output.mp3", "wb") as out:
        out.write(response.audio_content)
    
    return "/tmp/tts_output.mp3"
```

**Option B: Azure Speech Services**
```python
import azure.cognitiveservices.speech as speechsdk

# ASR
def transcribe_audio_azure(audio_file):
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_KEY"),
        region=os.getenv("AZURE_SPEECH_REGION")
    )
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )
    result = recognizer.recognize_once()
    return result.text

# TTS
def synthesize_speech_azure(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_KEY"),
        region=os.getenv("AZURE_SPEECH_REGION")
    )
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = synthesizer.speak_text_async(text).get()
    
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return result.audio_data
```

**Option C: AWS Polly & Transcribe**
```python
import boto3

# ASR
def transcribe_audio_aws(audio_file):
    transcribe = boto3.client('transcribe')
    job_name = f"transcribe_{uuid.uuid4()}"
    
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': f"s3://bucket/{audio_file}"},
        MediaFormat='wav',
        LanguageCode='en-US'
    )
    
    # Poll for completion
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)
    
    # Get transcript
    transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
    # Download and parse JSON
    return transcript

# TTS
def synthesize_speech_aws(text):
    polly = boto3.client('polly')
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Joanna'
    )
    
    with open('/tmp/tts_output.mp3', 'wb') as f:
        f.write(response['AudioStream'].read())
    
    return '/tmp/tts_output.mp3'
```

#### 4. **Call Flow Control**

**Instead of TwiML, use FreeSWITCH Dialplan or ESL:**

```python
# Real-time call control via ESL
def handle_call_flow(call_uuid, user_input):
    con = freeswitchESL.ESLconnection("127.0.0.1", "8021", "ClueCon")
    
    # Process user input with conversation engine
    response = process_with_agent(user_input, user_id)
    
    # Convert response to speech
    tts_file = synthesize_speech(response)
    
    # Play response
    con.execute("playback", tts_file, call_uuid)
    
    # Record next user input
    con.execute("record_session", "/tmp/next_input.wav", call_uuid)
    
    return True
```

**Or use mod_audio_fork for streaming ASR:**
```xml
<!-- FreeSWITCH dialplan with mod_audio_fork -->
<action application="set" data="audio_fork=shout://your-asr-service/stream"/>
<action application="record_session" data="/tmp/call.wav"/>
```

---

## Option 2: Hybrid Approach - FusionPBX + External ASR/TTS

### Overview
Use FusionPBX for call control, but keep external ASR/TTS services (Google, Azure, AWS).

### Benefits
- No Twilio dependency
- Use best-in-class ASR/TTS services
- Lower costs than Twilio
- Full control over call routing

### Architecture

```
DID → FusionPBX → Your App → Google/Azure ASR/TTS
                    ↓
              Conversation Engine
                    ↓
              Google/Azure TTS → FusionPBX → User
```

---

## Option 3: SIP Provider with Direct Integration

### Providers to Consider

1. **Telnyx**
   - Direct SIP trunking
   - REST API for call control
   - Built-in ASR/TTS options
   - Competitive pricing

2. **Flowroute**
   - SIP trunking
   - Simple API
   - Good for US/Canada

3. **VoIP.ms**
   - Affordable SIP trunking
   - Good for small scale

4. **Bandwidth**
   - Enterprise-grade
   - Direct SIP integration
   - Good for scale

### Implementation Example (Telnyx)

```python
import requests

# Inbound call handling
@app.route('/telnyx/webhook', methods=['POST'])
def telnyx_webhook():
    data = request.json
    call_control_id = data['data']['payload']['call_control_id']
    
    # Answer call
    requests.post(
        f"https://api.telnyx.com/v2/calls/{call_control_id}/actions/answer",
        headers={"Authorization": f"Bearer {TELNYX_API_KEY}"}
    )
    
    # Start recording for ASR
    requests.post(
        f"https://api.telnyx.com/v2/calls/{call_control_id}/actions/record_start",
        headers={"Authorization": f"Bearer {TELNYX_API_KEY}"}
    )
    
    return jsonify({"status": "ok"})

# Outbound calls
def initiate_transfer_telnyx(extension, user_number):
    # Create call to agent
    response = requests.post(
        "https://api.telnyx.com/v2/calls",
        headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
        json={
            "connection_id": TELNYX_CONNECTION_ID,
            "to": f"sip:{extension}@{freepbx_domain}",
            "from": CALLER_ID
        }
    )
    
    return response.json()
```

---

## Cost Comparison

### Twilio (Current)
- Inbound: ~$0.0085/min
- Outbound: ~$0.013/min
- ASR: ~$0.02/min
- TTS: ~$0.016/min
- **Total per call**: ~$0.06/min

### FusionPBX + Google Cloud
- DID: ~$1-5/month per number
- Google ASR: ~$0.006/min
- Google TTS: ~$0.004/min
- **Total per call**: ~$0.01/min
- **Savings**: ~83% reduction

### FusionPBX + Azure
- DID: ~$1-5/month per number
- Azure ASR: ~$0.01/min
- Azure TTS: ~$0.015/min
- **Total per call**: ~$0.025/min
- **Savings**: ~58% reduction

---

## Migration Strategy

### Phase 1: Setup FusionPBX Integration
1. Configure DID trunk in FusionPBX
2. Set up FreeSWITCH ESL connection
3. Create inbound route to your application
4. Test basic call handling

### Phase 2: Replace ASR/TTS
1. Integrate Google/Azure/AWS ASR
2. Integrate Google/Azure/AWS TTS
3. Test transcription and synthesis quality
4. Compare with Twilio quality

### Phase 3: Replace Outbound Calls
1. Implement FreeSWITCH originate for agent calls
2. Implement FreeSWITCH originate for user calls
3. Test transfer scenarios
4. Update call center integration

### Phase 4: Remove Twilio
1. Update all routes to use FusionPBX
2. Remove Twilio dependencies
3. Update configuration
4. Monitor and optimize

---

## Code Changes Required

### 1. Update `webrtc_voice_server.py`

**Replace:**
```python
from twilio.rest import Client

def initiate_agent_transfer(extension, session_data, session_id=None):
    client = Client(account_sid, auth_token)
    agent_call = client.calls.create(...)
```

**With:**
```python
import freeswitchESL

def initiate_agent_transfer(extension, session_data, session_id=None):
    con = freeswitchESL.ESLconnection("127.0.0.1", "8021", "ClueCon")
    # Use FreeSWITCH ESL for call origination
```

### 2. Update `routes.py`

**Replace:**
```python
@convonet_todo_bp.route('/twilio/call', methods=['POST'])
def twilio_call_webhook():
    response = VoiceResponse()
    # TwiML generation
```

**With:**
```python
@convonet_todo_bp.route('/freeswitch/call', methods=['POST'])
def freeswitch_call_webhook():
    # Handle via ESL or dialplan
    # Process audio directly
```

### 3. Add ASR/TTS Integration

**New file: `convonet/asr_tts_service.py`:**
```python
from google.cloud import speech, texttospeech

class ASRTTSService:
    def __init__(self, provider='google'):
        self.provider = provider
        if provider == 'google':
            self.asr_client = speech.SpeechClient()
            self.tts_client = texttospeech.TextToSpeechClient()
    
    def transcribe(self, audio_file):
        # Implementation
        pass
    
    def synthesize(self, text):
        # Implementation
        pass
```

---

## Recommended Approach

**For your use case, I recommend:**

1. **Use FusionPBX directly** for all call control (inbound and outbound)
2. **Use Google Cloud Speech-to-Text** for ASR (best accuracy, good pricing)
3. **Use Google Cloud Text-to-Speech** for TTS (natural voices, good pricing)
4. **Keep your existing conversation engine** (no changes needed)

**Benefits:**
- ✅ Eliminates Twilio dependency
- ✅ Lower costs (~83% reduction)
- ✅ Full control over call routing
- ✅ Better integration with your existing FusionPBX infrastructure
- ✅ More flexible for custom features

**Trade-offs:**
- ⚠️ More setup required (DID trunk, ESL integration)
- ⚠️ Need to manage ASR/TTS service accounts
- ⚠️ Slightly more complex error handling

---

## Next Steps

1. **Test FreeSWITCH ESL connection** to your FusionPBX
2. **Set up Google Cloud Speech/TTS** accounts
3. **Create proof-of-concept** for one call flow
4. **Compare quality** with current Twilio implementation
5. **Plan migration** in phases

Would you like me to create a detailed implementation guide for any of these options?

