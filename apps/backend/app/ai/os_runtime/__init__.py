"""AI Operating System Core, Always-On Voice Runtime & Continuous Cognitive Engine package.

Exposes configuration, models, interfaces, exceptions, wake-word engine, VAD, streaming STT,
voice authentication, streaming conversation engine, interruption engine, voice session manager,
contextual awareness engine, confirmation engine, voice notification engine, hands-free computing,
15-agent voice workforce, background mission support, system tray application, voice observability,
and central NovaOperatingSystemEngine facade.
"""

from typing import Any
from app.ai.os_runtime.utils import lazy_import

__all__ = [
    "OSRuntimeConfiguration",
    "OSState",
    "SubsystemStatus",
    "VoiceUserRole",
    "VADState",
    "OSBootDiagnostic",
    "WakeWordDetection",
    "VoicePrintVerification",
    "PartialTranscript",
    "EarlyReasoningResult",
    "ConfirmationHold",
    "ProactiveVoiceNotification",
    "SystemTrayStatus",
    "VoiceAgentBlueprint",
    "MissionCheckpoint",
    "OSHealth",
    "IWakeWordEngine",
    "IVoiceActivityDetector",
    "IStreamingSpeechRecognition",
    "IVoiceAuthenticator",
    "IStreamingConversationEngine",
    "IInterruptionEngine",
    "IConfirmationEngine",
    "IVoiceNotificationEngine",
    "IBackgroundMissionSupport",
    "ISystemTrayRuntime",
    "IVoiceAgentWorkforce",
    "INovaOperatingSystemEngine",
    "OSRuntimeError",
    "VoiceAuthFailedError",
    "ConfirmationDeniedError",
    "MicrophoneUnavailableError",
    "MissionCheckpointError",
    "WakeWordEngine",
    "VoiceActivityDetector",
    "StreamingSpeechRecognition",
    "VoiceAuthenticator",
    "StreamingConversationEngine",
    "InterruptionEngine",
    "VoiceSessionManager",
    "ContextAwarenessEngine",
    "ConfirmationEngine",
    "VoiceNotificationEngine",
    "HandsFreeComputingEngine",
    "VoiceAgentWorkforce",
    "BackgroundMissionSupport",
    "SystemTrayRuntime",
    "VoiceObservabilityMetrics",
    "BootManager",
    "LifecycleManager",
    "WindowsServiceManager",
    "StartupManager",
    "AlwaysOnVoiceRuntime",
    "OSRuntimeManagerFacade",
    "NovaOperatingSystemEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
