"""PEP 562 Lazy Import Utility Mapping for Ambient package."""

import importlib
from typing import Any

_LAZY_MAP: dict = {
    # Core Config & Models
    "AmbientConfiguration": "app.ai.ambient.configuration",
    "AmbientState": "app.ai.ambient.models",
    "WakeWordType": "app.ai.ambient.models",
    "InterruptionPolicy": "app.ai.ambient.models",
    "PrivacyLevel": "app.ai.ambient.models",
    "ConversationState": "app.ai.ambient.models",
    "AudioFrame": "app.ai.ambient.models",
    "WakeWordMatch": "app.ai.ambient.models",
    "ActiveWindowInfo": "app.ai.ambient.models",
    "ClipboardContent": "app.ai.ambient.models",
    "NotificationEvent": "app.ai.ambient.models",
    "DesktopContextSnapshot": "app.ai.ambient.models",
    "ProactiveSuggestion": "app.ai.ambient.models",
    "ConversationTurn": "app.ai.ambient.models",
    "VoiceSessionRecord": "app.ai.ambient.models",
    "AmbientMetrics": "app.ai.ambient.models",
    "AmbientHealth": "app.ai.ambient.models",
    # Interfaces
    "IMicrophoneListener": "app.ai.ambient.interfaces",
    "IWakeWordRuntime": "app.ai.ambient.interfaces",
    "IConversationManager": "app.ai.ambient.interfaces",
    "IDesktopContextMonitor": "app.ai.ambient.interfaces",
    "IProactiveAssistant": "app.ai.ambient.interfaces",
    "IAmbientEngine": "app.ai.ambient.interfaces",
    # Exceptions
    "AmbientEngineError": "app.ai.ambient.exceptions",
    "MicrophoneError": "app.ai.ambient.exceptions",
    "WakeWordDetectionError": "app.ai.ambient.exceptions",
    "PrivacyModeError": "app.ai.ambient.exceptions",
    "ConversationSessionError": "app.ai.ambient.exceptions",
    # Sub-systems & Managers
    "MicrophoneListener": "app.ai.ambient.microphone_listener",
    "AudioStream": "app.ai.ambient.audio_stream",
    "WakeWordRuntime": "app.ai.ambient.wake_word_runtime",
    "ConversationManager": "app.ai.ambient.conversation_manager",
    "ConversationHistory": "app.ai.ambient.conversation_history",
    "ConversationContext": "app.ai.ambient.conversation_context",
    "DesktopContext": "app.ai.ambient.desktop_context",
    "ActiveWindowMonitor": "app.ai.ambient.active_window_monitor",
    "ClipboardMonitor": "app.ai.ambient.clipboard_monitor",
    "NotificationMonitor": "app.ai.ambient.notification_monitor",
    "ScreenContext": "app.ai.ambient.screen_context",
    "ApplicationMonitor": "app.ai.ambient.application_monitor",
    "IdleDetector": "app.ai.ambient.idle_detector",
    "PresenceDetector": "app.ai.ambient.presence_detector",
    "AttentionManager": "app.ai.ambient.attention_manager",
    "InterruptionManager": "app.ai.ambient.interruption_manager",
    "ProactiveAssistant": "app.ai.ambient.proactive_assistant",
    "ConversationMemory": "app.ai.ambient.conversation_memory",
    "VoiceSession": "app.ai.ambient.voice_session",
    "SpeechPipeline": "app.ai.ambient.speech_pipeline",
    "ContextPipeline": "app.ai.ambient.context_pipeline",
    "AmbientScheduler": "app.ai.ambient.ambient_scheduler",
    "AmbientManager": "app.ai.ambient.ambient_manager",
    "AmbientEngine": "app.ai.ambient.ambient_engine",
    # Metrics, Health, Cache & Providers
    "AmbientMetricsTracker": "app.ai.ambient.metrics",
    "AmbientHealthMonitor": "app.ai.ambient.health",
    "AmbientCache": "app.ai.ambient.cache",
    "MockAmbientProvider": "app.ai.ambient.mock_provider",
}


def lazy_import(name: str) -> Any:
    """Dynamically imports a mapped class or utility by name."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"Attribute '{name}' not found in ambient lazy mapping.")
