"""Abstract base interfaces and contracts for AI Operating System Core, Always-On Voice Runtime & Continuous Cognitive Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional
from app.ai.os_runtime.models import (
    ConfirmationHold,
    EarlyReasoningResult,
    MissionCheckpoint,
    OSHealth,
    PartialTranscript,
    ProactiveVoiceNotification,
    SystemTrayStatus,
    VADState,
    VoiceAgentBlueprint,
    VoicePrintVerification,
    WakeWordDetection,
)


class IWakeWordEngine(ABC):
    """Contract for wake-word detection engine."""

    @abstractmethod
    async def process_audio_chunk(self, audio_chunk: bytes) -> WakeWordDetection:
        """Processes continuous audio stream chunk for wake word."""
        pass


class IVoiceActivityDetector(ABC):
    """Contract for Voice Activity Detection."""

    @abstractmethod
    def detect_vad(self, audio_chunk: bytes) -> VADState:
        """Determines speech/silence state bounds."""
        pass


class IStreamingSpeechRecognition(ABC):
    """Contract for real-time streaming STT."""

    @abstractmethod
    async def transcribe_stream(self, audio_generator: Any) -> AsyncGenerator[PartialTranscript, None]:
        """Streams real-time incremental transcription tokens."""
        pass


class IVoiceAuthenticator(ABC):
    """Contract for voice print verification."""

    @abstractmethod
    async def verify_speaker(self, audio_sample: bytes) -> VoicePrintVerification:
        """Verifies speaker voice print against registered owner profile."""
        pass


class IStreamingConversationEngine(ABC):
    """Contract for speculative early reasoning on partial transcription."""

    @abstractmethod
    async def evaluate_partial(self, partial_text: str) -> EarlyReasoningResult:
        """Initiates early reasoning before user finishes speaking."""
        pass


class IInterruptionEngine(ABC):
    """Contract for speech barge-in interrupt handling."""

    @abstractmethod
    async def handle_barge_in(self) -> bool:
        """Immediately pauses TTS output and prepares for new voice input."""
        pass


class IConfirmationEngine(ABC):
    """Contract for safety confirmation holds."""

    @abstractmethod
    async def request_confirmation(self, action_type: str, description: str) -> ConfirmationHold:
        """Places confirmation hold on sensitive OS action."""
        pass

    @abstractmethod
    async def approve_confirmation(self, hold_id: str) -> bool:
        """Approves pending confirmation hold."""
        pass


class IVoiceNotificationEngine(ABC):
    """Contract for proactive voice notification dispatching."""

    @abstractmethod
    async def notify_voice(self, title: str, message: str) -> ProactiveVoiceNotification:
        """Dispatches proactive voice notification alert."""
        pass


class IBackgroundMissionSupport(ABC):
    """Contract for long-running background mission management."""

    @abstractmethod
    async def create_checkpoint(self, mission_id: str, name: str, progress: float, step: str) -> MissionCheckpoint:
        """Saves background mission checkpoint."""
        pass

    @abstractmethod
    async def recover_missions_after_reboot(self) -> List[MissionCheckpoint]:
        """Restores background missions after OS reboot."""
        pass


class ISystemTrayRuntime(ABC):
    """Contract for Windows System Tray daemon."""

    @abstractmethod
    def get_tray_status(self) -> SystemTrayStatus:
        """Returns current system tray status snapshot."""
        pass

    @abstractmethod
    def toggle_mute(self) -> bool:
        """Toggles microphone mute status."""
        pass


class IVoiceAgentWorkforce(ABC):
    """Contract for 15-Agent Voice Workforce."""

    @abstractmethod
    def list_agents(self) -> List[VoiceAgentBlueprint]:
        """Lists active voice workforce agents."""
        pass


class INovaOperatingSystemEngine(ABC):
    """Central OS background runtime heartbeat contract."""

    @abstractmethod
    async def boot_system(self) -> bool:
        """Boots background OS runtime and initializes all 25 subsystems."""
        pass

    @abstractmethod
    async def process_voice_turn(self, audio_sample: bytes) -> Dict[str, Any]:
        """Executes complete voice turn: Wake -> VAD -> STT -> Early Reason -> Orchestrator -> Action -> TTS."""
        pass

    @abstractmethod
    def get_os_health(self) -> OSHealth:
        """Snapshot OS background runtime health metrics."""
        pass
