"""OS Runtime Manager Facade serving as high-level administrative runtime controller.
"""

from typing import Any, Dict, Optional
from app.ai.os_runtime.background_mission_support import BackgroundMissionSupport
from app.ai.os_runtime.configuration import OSRuntimeConfiguration
from app.ai.os_runtime.confirmation_engine import ConfirmationEngine
from app.ai.os_runtime.context_awareness_engine import ContextAwarenessEngine
from app.ai.os_runtime.hands_free_computing import HandsFreeComputingEngine
from app.ai.os_runtime.interruption_engine import InterruptionEngine
from app.ai.os_runtime.streaming_conversation_engine import StreamingConversationEngine
from app.ai.os_runtime.streaming_stt import StreamingSpeechRecognition
from app.ai.os_runtime.system_tray_runtime import SystemTrayRuntime
from app.ai.os_runtime.voice_activity_detector import VoiceActivityDetector
from app.ai.os_runtime.voice_agent_workforce import VoiceAgentWorkforce
from app.ai.os_runtime.voice_authenticator import VoiceAuthenticator
from app.ai.os_runtime.voice_notification_engine import VoiceNotificationEngine
from app.ai.os_runtime.voice_observability import VoiceObservabilityMetrics
from app.ai.os_runtime.voice_session_manager import VoiceSessionManager
from app.ai.os_runtime.wake_word_engine import WakeWordEngine


class OSRuntimeManagerFacade:
    """High-level administrative controller for Nova AI Operating System runtime."""

    def __init__(self, config: Optional[OSRuntimeConfiguration] = None) -> None:
        self.config = config or OSRuntimeConfiguration()
        self._is_started = False

        self.wake_word_engine = WakeWordEngine(primary_phrase=self.config.wake_word)
        self.vad = VoiceActivityDetector(sensitivity=self.config.vad_sensitivity)
        self.stt = StreamingSpeechRecognition(model_name=self.config.stt_model)
        self.voice_auth = VoiceAuthenticator(owner_voice_id=self.config.owner_voice_id)
        self.conversation_engine = StreamingConversationEngine()
        self.interruption_engine = InterruptionEngine()
        self.session_manager = VoiceSessionManager()
        self.context_engine = ContextAwarenessEngine()
        self.confirmation_engine = ConfirmationEngine()
        self.notification_engine = VoiceNotificationEngine()
        self.hands_free_engine = HandsFreeComputingEngine()
        self.agent_workforce = VoiceAgentWorkforce()
        self.mission_support = BackgroundMissionSupport()
        self.system_tray = SystemTrayRuntime()
        self.observability = VoiceObservabilityMetrics()

    async def start(self) -> None:
        """Starts OS runtime manager."""
        self._is_started = True

    async def stop(self) -> None:
        """Stops OS runtime manager."""
        self._is_started = False
