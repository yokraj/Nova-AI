"""Conversation History tracker recording turns, generating summaries, and replaying history.
"""

from typing import Any, Dict, List
from app.ai.conversation.models import ConversationSession, ConversationTurn, ConversationTurnRole


class ConversationHistoryTracker:
    """Records turn history, summarizes past interactions, and formats history arrays."""

    def add_turn(self, session: ConversationSession, role: ConversationTurnRole, text: str) -> ConversationTurn:
        """Appends new turn to session history.

        Args:
            session: ConversationSession instance.
            role: ConversationTurnRole enum (USER, ASSISTANT, SYSTEM).
            text: Utterance text string.

        Returns:
            Appended ConversationTurn instance.
        """
        turn = ConversationTurn(role=role, text=text)
        session.turns.append(turn)
        return turn

    def summarize_history(self, session: ConversationSession) -> str:
        """Generates concise summary of turn history.

        Args:
            session: Target ConversationSession instance.

        Returns:
            Summary paragraph string.
        """
        if not session.turns:
            return "No previous conversation history."
        user_turns = [t.text for t in session.turns if t.role == ConversationTurnRole.USER]
        return f"Conversation session contains {len(session.turns)} turns covering topics: '{' | '.join(user_turns[-3:])}'."

    def format_history_list(self, session: ConversationSession) -> List[Dict[str, Any]]:
        """Formats turn history as list of dictionaries."""
        return [
            {
                "turn_id": t.turn_id,
                "role": t.role.value,
                "text": t.text,
                "timestamp": t.timestamp,
                "emotion": t.emotion.primary_emotion.value,
            }
            for t in session.turns
        ]
