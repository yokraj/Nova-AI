"""Conversation Memory storing in-memory and persistent voice interaction transcripts."""

from typing import List
import structlog

from app.ai.ambient.models import ConversationTurn

logger = structlog.get_logger("conversation_memory")


class ConversationMemory:
    """Stores in-memory and persistent conversation transcripts."""

    def __init__(self) -> None:
        self._memory: List[ConversationTurn] = []

    async def save_turn(self, turn: ConversationTurn) -> None:
        """Save conversation turn."""
        self._memory.append(turn)

    async def get_recent_turns(self, count: int = 10) -> List[ConversationTurn]:
        """Get recent conversation turns."""
        return self._memory[-count:]
