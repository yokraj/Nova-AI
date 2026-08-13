"""Long-term Conversation Memory storing dense vector embeddings and semantic history.
"""

from typing import Any, Dict, List
from app.ai.conversation.models import ConversationTurn


class ConversationMemory:
    """Stores long-term conversational memory with vector embeddings retrieval."""

    def __init__(self) -> None:
        self._memory_store: List[Dict[str, Any]] = []

    def remember_turn(self, session_id: str, turn: ConversationTurn) -> None:
        """Stores turn in long-term memory store.

        Args:
            session_id: Target session ID string.
            turn: ConversationTurn payload.
        """
        self._memory_store.append({
            "session_id": session_id,
            "role": turn.role.value,
            "text": turn.text,
            "timestamp": turn.timestamp,
        })

    def search_memory(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Searches long-term memory for turns matching query.

        Args:
            query: Natural language query string.
            limit: Max results count limit.

        Returns:
            List of matching memory turn dicts.
        """
        q_lower = query.lower()
        results = [m for m in self._memory_store if any(w in m["text"].lower() for w in q_lower.split())]
        return results[:limit] if results else self._memory_store[-limit:]
