---
name: nova-voice
description: >-
  Development and verification runbook for Nova-AI voice input, speech-to-text (STT), text-to-speech (TTS), command routing, security filtering, and real voice execution.
---

# Nova Voice Subsystem Skill

Use this skill when developing, testing, or auditing voice input pipelines, wake word detection, local Whisper STT integration, voice command execution, or TTS feedback in Nova-AI.

## Subsystem Architecture Overview

The voice engine resides in `apps/backend/app/voice/`:
- `voice/stt_service.py`: Local speech-to-text using Faster-Whisper / OpenAI Whisper local models.
- `voice/tts_service.py`: Text-to-speech synthesis (e.g. Piper, Coqui TTS, Pyttsx3 local drivers).
- `voice/wake_word.py`: Wake word listener (pvporcupine / openWakeWord).
- `voice/always_on_runtime.py`: Always-on voice listening daemon.
- `apps/frontend/src/components/voice/`: Web Speech API / Audio Worklet recorder UI components.

## Development & Verification Procedures

### 1. Speech-to-Text (STT) Integration
- Default to local Whisper models (`tiny.en`, `base.en`, `small.en`) to maintain zero cloud dependency.
- Validate audio input stream format: 16kHz, single-channel 16-bit PCM WAV audio.

### 2. Voice Command Security Pipeline
- Voice transcripts must pass through the Security & Prompt Injection pipeline (`PromptInjectionFilter.detect_injection`) BEFORE reaching the AI orchestrator or command executor.
- Prevent voice injection attacks (e.g., played back audio attempting to execute unauthorized shell or system commands).

### 3. Voice Execution Verification
- Test always-on voice runtime using the dedicated test harness:
  ```powershell
  python test_always_on_voice_runtime_manual.py
  ```
- Verify audio device availability, microphone permission access, wake-word activation latency, and transcript accuracy.
