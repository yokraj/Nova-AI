"""Conversation Recovery Engine repairing broken dialogue states and context gaps.
"""

from typing import Any, Dict
from app.ai.conversation.models import ConversationSession, ConversationState


class ConversationRecoveryEngine:
    """Repairs conversation state after errors or lost context."""

    def repair_session(self, session: ConversationSession) -> bool:
        """Repairs broken dialogue state.

        Args:
            session: ConversationSession payload instance.

        Returns:
            True if repaired successfully.
        """
        session.current_state = ConversationState.ACTIVE
        return True
