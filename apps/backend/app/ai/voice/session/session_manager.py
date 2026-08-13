"""Voice Session Manager tracks live session sessions and conversation state.
"""

from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict
from app.ai.voice.interfaces import IVoiceSessionManager
from app.ai.voice.models import VoiceSession
from app.ai.voice.exceptions import VoiceSessionError

class VoiceSessionManager(IVoiceSessionManager):
    """Tracks active sessions, session histories, and connects to the memory system."""

    def __init__(self) -> None:
        self.active_sessions: Dict[str, VoiceSession] = {}

    def create_session(self) -> VoiceSession:
        """Initializes a new listener session."""
        session = VoiceSession()
        self.active_sessions[str(session.id)] = session
        return session

    def close_session(self, session_id: UUID) -> None:
        """Closes session records."""
        str_id = str(session_id)
        if str_id in self.active_sessions:
            session = self.active_sessions[str_id]
            session.end_time = datetime.now(timezone.utc)
            session.status = "closed"
            del self.active_sessions[str_id]
        else:
            raise VoiceSessionError(f"Session '{session_id}' not found.")
