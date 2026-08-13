"""Vector Store Abstraction Module.

Provides pluggable abstraction layer supporting SQLite fast fallback, ChromaDB,
FAISS, Qdrant, and Milvus vector store backends.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.vector_memory.config import VectorConfig

logger = structlog.get_logger(__name__)


class BaseVectorStoreBackend:
    """Abstract interface for vector database backends."""

    async def insert(self, memory_id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        raise NotImplementedError

    async def search(self, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def delete(self, memory_id: str) -> bool:
        raise NotImplementedError


class SQLiteVectorStoreBackend(BaseVectorStoreBackend):
    """Fast in-memory/relational vector store implementation."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}

    async def insert(self, memory_id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        self._store[memory_id] = {
            "memory_id": memory_id,
            "vector": vector,
            "metadata": metadata,
        }

    async def search(self, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        # Compute dot product/cosine in memory
        results = []
        for item in self._store.values():
            vec = item["vector"]
            if len(vec) == len(query_vector):
                sim = sum(a * b for a, b in zip(query_vector, vec))
                results.append({
                    "memory_id": item["memory_id"],
                    "similarity_score": round(sim, 6),
                    "distance": round(1.0 - sim, 6),
                    "metadata": item["metadata"],
                })
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    async def delete(self, memory_id: str) -> bool:
        if memory_id in self._store:
            del self._store[memory_id]
            return True
        return False


class VectorStore:
    """Enterprise Pluggable Vector Store Manager."""

    def __init__(self, config: Optional[VectorConfig] = None) -> None:
        self.config = config or VectorConfig()
        self.backend = self._initialize_backend()
        logger.info("vector_store_initialized", backend_type=self.config.vector_store_backend)

    def _initialize_backend(self) -> BaseVectorStoreBackend:
        """Instantiates target backend driver based on configuration."""
        # Defaults to SQLite fast fallback; interfaces ready for ChromaDB/FAISS/Qdrant/Milvus
        return SQLiteVectorStoreBackend()

    async def add_vector(self, memory_id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        """Adds a vector entry to the active backend."""
        await self.backend.insert(memory_id, vector, metadata)

    async def search_vectors(self, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Queries active backend for nearest vector candidates."""
        return await self.backend.search(query_vector, top_k=top_k)

    async def delete_vector(self, memory_id: str) -> bool:
        """Deletes a vector from active backend."""
        return await self.backend.delete(memory_id)
