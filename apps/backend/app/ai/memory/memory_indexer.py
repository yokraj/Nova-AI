"""Memory Indexer indexes chunks and vectors into active store databases.
"""

from typing import List
from uuid import UUID
from app.ai.memory.vector_store import IVectorStore
from app.ai.memory.embedding_manager import EmbeddingManager
from app.ai.memory.models import MemoryItem, DocumentChunk, MemoryType

class MemoryIndexer:
    """Orchestrates embedding creation and node storage inside vector databases."""

    def __init__(self, store: IVectorStore, embedding_mgr: EmbeddingManager) -> None:
        self.store = store
        self.embedding_mgr = embedding_mgr

    async def index_chunks(self, chunks: List[DocumentChunk], m_type: MemoryType = MemoryType.DOCUMENT) -> None:
        """Generates vectors for chunks and registers them to the active store."""
        items = []
        for chunk in chunks:
            vector = await self.embedding_mgr.embed_text(chunk.content)
            
            # Combine original chunk metadata
            meta = chunk.metadata.copy()
            meta["document_id"] = chunk.document_id
            meta["chunk_index"] = chunk.chunk_index
            meta["source"] = chunk.document_id

            items.append(
                MemoryItem(
                    content=chunk.content,
                    memory_type=m_type,
                    metadata=meta,
                    embedding=vector
                )
            )

        if items:
            await self.store.add(items)

    async def remove_stale_entry(self, item_id: UUID) -> None:
        """Deletes a node from index."""
        await self.store.delete(item_id)
