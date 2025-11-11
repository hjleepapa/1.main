# AssemblyAI Integration Modules

This repository includes a small set of helper modules for experimenting with AssemblyAI’s transcription stack,
primarily around adapting WebRTC audio into something the service can consume.
Use the files together when you need to plug AssemblyAI in place of the default Deepgram pipeline.

## `assemblyai_config.py`

- centralises configuration constants and utility helpers shared by the rest of the AssemblyAI scripts
- loads API credentials from the environment and exposes typed accessors
- safe place to add any global feature flags (streaming vs. file uploads, model selection, etc.)

## `assemblyai_service.py`

- wraps the official `assemblyai` Python SDK
- exposes a `AssemblyAIService` class with helper methods for converting raw audio buffers into text
- contains diagnostics explaining the pitfalls of feeding tiny WebRTC frames to the file-based API
- recommend reading the inline logging statements before using it in production – they highlight why streaming STT is usually a better fit

## `assemblyai_webrtc_integration.py`

- bridges the Flask/WebRTC layer with `AssemblyAIService`
- normalises audio chunks coming from the browser, performs quality checks, and hands them off for transcription
- demonstrates how to return the transcript back to the Socket.IO client while leaving Deepgram wired in as the primary engine

### Usage Tips

1. Set `ASSEMBLYAI_API_KEY` in your environment before instantiating `AssemblyAIService`.
2. Start with short offline WAVs (see comments in `assemblyai_service.py`) to confirm the SDK works end-to-end.
3. Once verified, experiment with the streaming API instead of the file-upload helper if you need true real-time results.
4. Keep Deepgram as the default until the streaming pipeline is solid—these modules are intended as a sandbox.


