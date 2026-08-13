"""Main Local RAG Memory Engine orchestrator.
"""

from typing import Optional, List
from uuid import UUID
from app.ai.memory.models import MemoryItem, MemoryType, ContextPackage
from app.ai.memory.configuration import MemoryConfiguration
from app.ai.memory.embedding_manager import EmbeddingManager
from app.ai.memory.pgvector_store import PGVectorStore
from app.ai.memory.faiss_store import FAISSVectorStore
from app.ai.memory.memory_indexer import MemoryIndexer
from app.ai.memory.retrieval_engine import RetrievalEngine
from app.ai.memory.conversation_memory import ConversationMemory
from app.ai.memory.project_memory import ProjectMemory
from app.ai.memory.code_memory import CodeMemory

class LocalMemoryEngine:
    """Combines embedding generators, vector databases (PGVector or FAISS), indexers, and retrieval pipelines."""

    def __init__(self, config: Optional[MemoryConfiguration] = None) -> None:
        self.config = config or MemoryConfiguration()
        self.embedding_mgr = EmbeddingManager(model_name=self.config.embedding_model)

        # Initialize target vector store with absolute fallback security
        self.store = None
        if self.config.vector_database == "pgvector":
            try:
                self.store = PGVectorStore()
            except Exception:
                # Fallback to FAISS if PostgreSQL context is unavailable
                pass

        if self.store is None:
            self.store = FAISSVectorStore(storage_path=self.config.storage_path)

        self.indexer = MemoryIndexer(self.store, self.embedding_mgr)
        self.retriever = RetrievalEngine(self.store, self.embedding_mgr)
        
        # Specialized engines
        self.conversation = ConversationMemory(self.store, self.embedding_mgr)
        self.project = ProjectMemory(self.store, self.embedding_mgr)
        self.code = CodeMemory(self.store, self.embedding_mgr)

    async def store_memory(self, content: str, memory_type: MemoryType, metadata: Optional[dict] = None) -> UUID:
        """Indexes content segments to RAG vector database."""
        vector = await self.embedding_mgr.embed_text(content)
        
        meta = metadata or {}
        meta["memory_type"] = memory_type.value

        item = MemoryItem(
            content=content,
            memory_type=memory_type,
            metadata=meta,
            embedding=vector
        )
        await self.store.add([item])
        return item.id

    async def retrieve_context(self, query: str, limit: int = 5) -> ContextPackage:
        """Retrieves and segments contexts matching query."""
        return await self.retriever.retrieve_context(
            query,
            limit=limit,
            threshold=self.config.similarity_threshold
        )

    async def count_memories(self) -> int:
        """Returns size of registered memories index."""
        return await self.store.count()
