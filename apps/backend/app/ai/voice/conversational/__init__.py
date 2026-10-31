"""Conversational Voice Assistant Package for Nova-AI (Phase 10M-B).
"""

from app.ai.voice.conversational.models import (
    AudioFrame,
    ConversationalSession,
    ConversationalState,
    ConversationalVoiceTurn,
    MicrophoneStatus,
    SpeechAnalysisResult,
    SpeechIntentType,
    VADState,
    WakeWordEvent,
    WakeWordMode,
)
from app.ai.voice.conversational.vad import VoiceActivityDetector
from app.ai.voice.conversational.audio_stream import StreamingAudioReceiver
from app.ai.voice.conversational.wake_word import ConversationalWakeWordEngine
from app.ai.voice.conversational.speech_intelligence import SpeechIntelligenceEngine
from app.ai.voice.conversational.echo_canceller import AcousticEchoCancellationGuard
from app.ai.voice.conversational.assistant import ConversationalVoiceAssistant

__all__ = [
    "AudioFrame",
    "ConversationalSession",
    "ConversationalState",
    "ConversationalVoiceTurn",
    "MicrophoneStatus",
    "SpeechAnalysisResult",
    "SpeechIntentType",
    "VADState",
    "WakeWordEvent",
    "WakeWordMode",
    "VoiceActivityDetector",
    "StreamingAudioReceiver",
    "ConversationalWakeWordEngine",
    "SpeechIntelligenceEngine",
    "AcousticEchoCancellationGuard",
    "ConversationalVoiceAssistant",
]

