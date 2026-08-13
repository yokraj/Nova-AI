"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.os_runtime.
"""

import importlib
from typing import Any, Dict

_LAZY_MAP: Dict[str, str] = {
    "OSRuntimeConfiguration": "app.ai.os_runtime.configuration",
    "OSState": "app.ai.os_runtime.models",
    "SubsystemStatus": "app.ai.os_runtime.models",
    "VoiceUserRole": "app.ai.os_runtime.models",
    "VADState": "app.ai.os_runtime.models",
    "OSBootDiagnostic": "app.ai.os_runtime.models",
    "WakeWordDetection": "app.ai.os_runtime.models",
    "VoicePrintVerification": "app.ai.os_runtime.models",
    "PartialTranscript": "app.ai.os_runtime.models",
    "EarlyReasoningResult": "app.ai.os_runtime.models",
    "ConfirmationHold": "app.ai.os_runtime.models",
    "ProactiveVoiceNotification": "app.ai.os_runtime.models",
    "SystemTrayStatus": "app.ai.os_runtime.models",
    "VoiceAgentBlueprint": "app.ai.os_runtime.models",
    "MissionCheckpoint": "app.ai.os_runtime.models",
    "OSHealth": "app.ai.os_runtime.models",
    "IWakeWordEngine": "app.ai.os_runtime.interfaces",
    "IVoiceActivityDetector": "app.ai.os_runtime.interfaces",
    "IStreamingSpeechRecognition": "app.ai.os_runtime.interfaces",
    "IVoiceAuthenticator": "app.ai.os_runtime.interfaces",
    "IStreamingConversationEngine": "app.ai.os_runtime.interfaces",
    "IInterruptionEngine": "app.ai.os_runtime.interfaces",
    "IConfirmationEngine": "app.ai.os_runtime.interfaces",
    "IVoiceNotificationEngine": "app.ai.os_runtime.interfaces",
    "IBackgroundMissionSupport": "app.ai.os_runtime.interfaces",
    "ISystemTrayRuntime": "app.ai.os_runtime.interfaces",
    "IVoiceAgentWorkforce": "app.ai.os_runtime.interfaces",
    "INovaOperatingSystemEngine": "app.ai.os_runtime.interfaces",
    "OSRuntimeError": "app.ai.os_runtime.exceptions",
    "VoiceAuthFailedError": "app.ai.os_runtime.exceptions",
    "ConfirmationDeniedError": "app.ai.os_runtime.exceptions",
    "MicrophoneUnavailableError": "app.ai.os_runtime.exceptions",
    "MissionCheckpointError": "app.ai.os_runtime.exceptions",
    "WakeWordEngine": "app.ai.os_runtime.wake_word_engine",
    "VoiceActivityDetector": "app.ai.os_runtime.voice_activity_detector",
    "StreamingSpeechRecognition": "app.ai.os_runtime.streaming_stt",
    "VoiceAuthenticator": "app.ai.os_runtime.voice_authenticator",
    "StreamingConversationEngine": "app.ai.os_runtime.streaming_conversation_engine",
    "InterruptionEngine": "app.ai.os_runtime.interruption_engine",
    "VoiceSessionManager": "app.ai.os_runtime.voice_session_manager",
    "ContextAwarenessEngine": "app.ai.os_runtime.context_awareness_engine",
    "ConfirmationEngine": "app.ai.os_runtime.confirmation_engine",
    "VoiceNotificationEngine": "app.ai.os_runtime.voice_notification_engine",
    "HandsFreeComputingEngine": "app.ai.os_runtime.hands_free_computing",
    "VoiceAgentWorkforce": "app.ai.os_runtime.voice_agent_workforce",
    "BackgroundMissionSupport": "app.ai.os_runtime.background_mission_support",
    "SystemTrayRuntime": "app.ai.os_runtime.system_tray_runtime",
    "VoiceObservabilityMetrics": "app.ai.os_runtime.voice_observability",
    "BootManager": "app.ai.os_runtime.boot_manager",
    "LifecycleManager": "app.ai.os_runtime.lifecycle_manager",
    "WindowsServiceManager": "app.ai.os_runtime.service_manager",
    "StartupManager": "app.ai.os_runtime.startup_manager",
    "AlwaysOnVoiceRuntime": "app.ai.os_runtime.voice_runtime",
    "OSRuntimeManagerFacade": "app.ai.os_runtime.manager",
    "NovaOperatingSystemEngine": "app.ai.os_runtime.engine",
}


def lazy_import(name: str) -> Any:
    """Dynamically imports symbol via PEP 562 lazy mapping."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
