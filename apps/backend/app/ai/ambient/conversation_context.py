"""Conversation Context tracking active topics, entities, and intent context."""

from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger("conversation_context")


class ConversationContext:
    """Tracks active conversational topics and referenced entities across turns."""

    def __init__(self) -> None:
        self._context: Dict[str, Any] = {
            "active_topic": "general_assistant",
            "last_mentioned_entity": None,
        }

    def update_context(self, key: str, value: Any) -> None:
        """Update conversational context key."""
        self._context[key] = value

    def get_context(self, key: str, default: Optional[Any] = None) -> Any:
        """Get conversational context value."""
        return self._context.get(key, default)
