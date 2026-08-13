"""Conversation Memory tracks user preferences and messages.
"""

from typing import List
from app.ai.memory.vector_store import IVectorStore
from app.ai.memory.embedding_manager import EmbeddingManager
from app.ai.memory.models import MemoryItem, MemoryType

class ConversationMemory:
    """Manages short-term and long-term conversation buffers."""

    def __init__(self, store: IVectorStore, embedding_mgr: EmbeddingManager) -> None:
        self.store = store
        self.embedding_mgr = embedding_mgr

    async def store_message(self, conversation_id: str, role: str, content: str) -> None:
        """Indexes a chat message to long-term memory."""
        vector = await self.embedding_mgr.embed_text(content)
        item = MemoryItem(
            content=f"{role.upper()}: {content}",
            memory_type=MemoryType.CONVERSATION,
            metadata={
                "conversation_id": conversation_id,
                "role": role,
                "memory_type": MemoryType.CONVERSATION.value
            },
            embedding=vector
        )
        await self.store.add([item])

    async def get_recent_decisions(self, conversation_id: str, limit: int = 5) -> List[str]:
        """Retrieves important decisions or content from this conversation session."""
        # Query matching vector representation of 'decision choice priority'
        q_vec = await self.embedding_mgr.embed_text("architecture stack decisions preferences")
        results = await self.store.search(q_vec, limit=limit, threshold=0.6)
        
        # Filter matching current conversation ID
        matches = []
        for r in results:
            if r.metadata.get("conversation_id") == conversation_id:
                matches.append(r.content)
        return matches
