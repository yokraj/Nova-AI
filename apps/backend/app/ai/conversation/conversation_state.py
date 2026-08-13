"""Conversation State machine tracking session state transitions, branching, and expiration.
"""

from typing import Dict, Optional
from app.ai.conversation.models import ConversationSession, ConversationState


class ConversationStateTracker:
    """Manages state transitions (ACTIVE, PAUSED, INTERRUPTED, STREAMING, COMPLETED, EXPIRED)."""

    def transition_state(self, session: ConversationSession, new_state: ConversationState) -> None:
        """Transitions conversation session state.

        Args:
            session: ConversationSession payload instance.
            new_state: Target ConversationState enum.
        """
        session.current_state = new_state

    def is_active(self, session: ConversationSession) -> bool:
        """Returns True if session is in ACTIVE or STREAMING state."""
        return session.current_state in (ConversationState.ACTIVE, ConversationState.STREAMING)
