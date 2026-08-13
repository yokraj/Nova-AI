"""Conversation Session Manager storing active sessions and turn histories.
"""

from typing import Dict, Optional
from app.ai.conversation.interfaces import IConversationManager
from app.ai.conversation.models import ConversationSession


class ConversationManager(IConversationManager):
    """Manages active conversation sessions lifecycle."""

    def __init__(self) -> None:
        self._sessions: Dict[str, ConversationSession] = {}

    def create_session(self, user_id: str = "user_primary") -> ConversationSession:
        """Creates and registers a new ConversationSession.

        Args:
            user_id: User identifier string.

        Returns:
            New ConversationSession instance.
        """
        sess = ConversationSession(user_id=user_id)
        self._sessions[sess.session_id] = sess
        return sess

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Retrieves session by session_id."""
        return self._sessions.get(session_id)

    def list_sessions(self) -> Dict[str, ConversationSession]:
        """Lists all active sessions."""
        return self._sessions
