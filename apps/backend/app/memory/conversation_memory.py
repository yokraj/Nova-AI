"""Conversation Memory Module.

Manages multi-turn conversation thread memories, turn history, and dialogue summarization.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.memory.repository import MemoryRepository
from app.memory.memory_compression import MemoryCompressor

logger = structlog.get_logger(__name__)


class ConversationMemoryManager:
    """Enterprise Conversation Memory Thread Manager."""

    def __init__(
        self,
        repository: MemoryRepository,
        compressor: Optional[MemoryCompressor] = None,
    ) -> None:
        self.repository = repository
        self.compressor = compressor or MemoryCompressor()
        logger.info("conversation_memory_manager_initialized")

    async def add_turn(
        self,
        conversation_id: str,
        role: str,
        content: str,
        workspace: str = "Nova",
        project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Appends a conversation message turn into conversation memory."""
        title = f"Conversation Turn [{conversation_id}]: {role}"
        entry = await self.repository.create_entry(
            title=title,
            content=content,
            summary=content[:100],
            memory_type="conversation",
            workspace=workspace,
            project=project,
            metadata_json={"conversation_id": conversation_id, "role": role},
        )
        logger.debug("conversation_turn_added", conversation_id=conversation_id, role=role)
        return {"memory_id": entry.id, "conversation_id": conversation_id, "role": role}

    async def get_history(self, conversation_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves recent conversation history for target conversation thread ID."""
        entries = await self.repository.search_entries(memory_type="conversation", limit=limit)
        history = []
        for e in entries:
            meta = e.metadata_json or {}
            if meta.get("conversation_id") == conversation_id:
                history.append({
                    "memory_id": e.id,
                    "role": meta.get("role", "user"),
                    "content": e.content,
                    "created_at": e.created_at.isoformat(),
                })
        return history
