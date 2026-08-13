"""Voice Session manager tracking active voice interaction sessions."""

from typing import Optional
import structlog

from app.ai.ambient.models import ConversationState, VoiceSessionRecord

logger = structlog.get_logger("voice_session")


class VoiceSession:
    """Manages an active voice session state and lifetime."""

    def __init__(self) -> None:
        self.session = VoiceSessionRecord()

    def end_session(self) -> None:
        """End voice session."""
        self.session.state = ConversationState.COMPLETED
        logger.info("Voice session completed", session_id=self.session.session_id)
