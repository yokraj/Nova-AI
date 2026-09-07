"""Voice Activation Manager handles wake word detection and session state lifecycle.
"""

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
import structlog

from app.ai.voice.wake_word.wake_word_detector import WakeWordDetector
from app.ai.voice.models import VoiceSession
from app.ai.voice.exceptions import WakeWordError

logger = structlog.get_logger("voice_activation")


class VoiceActivationManager:
    """Manages wake word listening loop and active voice session lifecycle."""

    def __init__(self, keyword: str = "Nova", timeout_sec: float = 30.0) -> None:
        self.detector = WakeWordDetector(keyword=keyword)
        self.timeout_sec = timeout_sec
        self.active_session: Optional[VoiceSession] = None
        self.is_active = False

    def process_audio_chunk(self, audio_chunk: bytes) -> bool:
        """Processes an audio chunk, triggering activation if keyword is detected."""
        if not audio_chunk:
            return False

        detected = self.detector.detect(audio_chunk)
        if detected:
            self.activate_session()
            return True
        return False

    def activate_session(self) -> VoiceSession:
        """Starts or refreshes an active voice interaction session."""
        self.active_session = VoiceSession(
            id=uuid4(),
            start_time=datetime.now(timezone.utc),
            status="active",
        )
        self.is_active = True
        logger.info("voice_session_activated", session_id=str(self.active_session.id))
        return self.active_session

    def deactivate_session(self) -> None:
        """Closes the current active session."""
        if self.active_session:
            self.active_session.end_time = datetime.now(timezone.utc)
            self.active_session.status = "closed"
            logger.info("voice_session_deactivated", session_id=str(self.active_session.id))
        self.is_active = False
        self.active_session = None

    def is_listening(self) -> bool:
        """Returns True if the activation system is currently active."""
        return self.is_active
