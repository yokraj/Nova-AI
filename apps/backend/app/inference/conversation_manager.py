"""Conversation Manager Module.

Manages conversation turn histories, message roles, and state for multi-turn inference.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ConversationManager:
    """Enterprise Multi-Turn Conversation Manager."""

    def __init__(self) -> None:
        self._conversations: Dict[str, List[Dict[str, str]]] = {}
        logger.info("conversation_manager_initialized")

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Appends a turn message to conversation state."""
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        self._conversations[conversation_id].append({"role": role, "content": content})

    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Retrieves conversation history turns."""
        return self._conversations.get(conversation_id, [])
