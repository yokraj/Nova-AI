"""Conversation History tracking historical voice conversation turns."""

from typing import List
import structlog

from app.ai.ambient.models import ConversationTurn

logger = structlog.get_logger("conversation_history")


class ConversationHistory:
    """Stores historical voice conversation turns."""

    def __init__(self) -> None:
        self._turns: List[ConversationTurn] = []

    def add_turn(self, speaker: str, text: str) -> ConversationTurn:
        """Record turn."""
        turn = ConversationTurn(speaker=speaker, text=text)
        self._turns.append(turn)
        return turn

    def list_turns(self) -> List[ConversationTurn]:
        """List past turns."""
        return list(self._turns)
