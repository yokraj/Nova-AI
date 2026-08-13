"""Interruption Manager handling human barge-in, response cancellation, pause, and resume.
"""

from typing import Dict
from app.ai.conversation.interfaces import IInterruptionManager


class InterruptionManager(IInterruptionManager):
    """Handles human barge-in events and cancels active audio playback streams."""

    def __init__(self) -> None:
        self._interrupted_sessions: Dict[str, bool] = {}

    def handle_interruption(self, session_id: str) -> bool:
        """Triggers cancellation signal for target session_id speech output.

        Args:
            session_id: Target session ID string.

        Returns:
            True if cancellation handled successfully.
        """
        self._interrupted_sessions[session_id] = True
        return True

    def was_interrupted(self, session_id: str) -> bool:
        """Returns True if session was interrupted by barge-in."""
        return self._interrupted_sessions.get(session_id, False)

    def reset_interruption(self, session_id: str) -> None:
        """Resets interruption flag for session."""
        if session_id in self._interrupted_sessions:
            del self._interrupted_sessions[session_id]
