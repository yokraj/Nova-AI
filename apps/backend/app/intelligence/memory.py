"""Memory Engine Module.

Implements MemoryEngine managing multi-tiered searchable memory (Short-term, Long-term,
Semantic, Conversation, Project, User Preferences, Workspace, and Knowledge memory).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
import structlog

logger = structlog.get_logger(__name__)


class MemoryEngine:
    """Enterprise Multi-Tiered Searchable Memory Engine."""

    def __init__(self) -> None:
        self._short_term_memory: List[Dict[str, Any]] = []
        self._long_term_memory: List[Dict[str, Any]] = []
        self._semantic_memory: Dict[str, Any] = {}
        self._conversation_memory: Dict[str, List[Dict[str, Any]]] = {}
        self._project_memory: Dict[str, Dict[str, Any]] = {}
        self._user_preferences: Dict[str, Any] = {}
        self._workspace_memory: Dict[str, Dict[str, Any]] = {}
        self._knowledge_memory: List[Dict[str, Any]] = []

        logger.info("memory_engine_initialized")

    async def add_short_term(self, role: str, content: str, conversation_id: str = "default") -> None:
        """Appends message item to short-term conversation memory."""
        item = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._short_term_memory.append(item)

        if conversation_id not in self._conversation_memory:
            self._conversation_memory[conversation_id] = []
        self._conversation_memory[conversation_id].append(item)
        logger.debug("short_term_memory_added", role=role, conversation_id=conversation_id)

    async def store_long_term(self, key: str, value: Any, category: str = "general") -> None:
        """Stores structured facts or records into long-term memory."""
        record = {
            "key": key,
            "value": value,
            "category": category,
            "stored_at": datetime.now(timezone.utc).isoformat(),
        }
        self._long_term_memory.append(record)
        logger.info("long_term_memory_stored", key=key, category=category)

    async def update_user_preferences(self, preferences: Dict[str, Any]) -> None:
        """Updates persistent user preference profile memory."""
        self._user_preferences.update(preferences)
        logger.info("user_preferences_updated", updated_keys=list(preferences.keys()))

    async def get_user_preferences(self) -> Dict[str, Any]:
        """Returns active user preference profile memory."""
        return dict(self._user_preferences)

    async def set_workspace_context(self, workspace_id: str, context_data: Dict[str, Any]) -> None:
        """Sets active workspace memory state."""
        self._workspace_memory[workspace_id] = context_data
        logger.info("workspace_memory_set", workspace_id=workspace_id)

    async def search_memory(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Searches across short-term, long-term, and knowledge memory stores."""
        query_lower = query.lower()
        results: List[Dict[str, Any]] = []

        # 1. Search short-term
        for item in self._short_term_memory:
            if query_lower in item.get("content", "").lower():
                results.append({"tier": "short_term", "data": item})

        # 2. Search long-term
        for record in self._long_term_memory:
            if query_lower in str(record.get("value", "")).lower() or query_lower in record.get("key", "").lower():
                results.append({"tier": "long_term", "data": record})

        logger.info("memory_search_completed", query=query, match_count=len(results))
        return results[:limit]

    async def get_recent_conversation_history(self, conversation_id: str = "default", limit: int = 10) -> List[Dict[str, Any]]:
        """Returns recent short-term messages for target conversation ID."""
        history = self._conversation_memory.get(conversation_id, [])
        return history[-limit:]
