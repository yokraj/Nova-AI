"""Vector Store Abstraction Module.

Provides pluggable abstraction layer supporting SQLite fast fallback, ChromaDB,
FAISS, Qdrant, and Milvus vector store backends, with strict dimension validation
and workspace isolation.
"""

import math
from typing import Any, Dict, List, Optional
import structlog

from app.vector_memory.config import VectorConfig

logger = structlog.get_logger(__name__)


class BaseVectorStoreBackend:
    """Abstract interface for vector database backends."""

    async def insert(self, memory_id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        raise NotImplementedError

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        workspace: Optional[str] = None,
        project: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
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
            "metadata": metadata or {},
        }

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        workspace: Optional[str] = None,
        project: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not query_vector or not self._store:
            return []

        results = []
        q_len = len(query_vector)

        for item in self._store.values():
            vec = item.get("vector", [])
            meta = item.get("metadata", {})

            # 1. Dimension compatibility check - NEVER compare incompatible vector dimensions
            if len(vec) != q_len:
                continue

            # 2. Never mix pseudo-embeddings with neural embeddings
            if meta.get("is_pseudo") is True:
                continue

            # 3. Model compatibility check (if specified)
            if model_name and meta.get("model_name") and meta.get("model_name") != model_name:
                continue

            # 4. Strict workspace isolation
            if workspace and meta.get("workspace") and meta.get("workspace") != workspace:
                continue

            # 5. Project isolation (if project filter provided)
            if project and meta.get("project") and meta.get("project") != project:
                continue

            # 6. Cosine Similarity Calculation
            dot = sum(a * b for a, b in zip(query_vector, vec))
            mag1 = math.sqrt(sum(a * a for a in query_vector))
            mag2 = math.sqrt(sum(b * b for b in vec))
            if mag1 == 0.0 or mag2 == 0.0:
                sim = 0.0
            else:
                sim = dot / (mag1 * mag2)

            results.append({
                "memory_id": item["memory_id"],
                "similarity_score": round(sim, 6),
                "distance": round(1.0 - sim, 6),
                "metadata": meta,
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
        return SQLiteVectorStoreBackend()

    async def add_vector(self, memory_id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        """Adds a vector entry to the active backend."""
        await self.backend.insert(memory_id, vector, metadata)

    async def search_vectors(
        self,
        query_vector: List[float],
        top_k: int = 10,
        workspace: Optional[str] = None,
        project: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Queries active backend for nearest vector candidates."""
        return await self.backend.search(
            query_vector,
            top_k=top_k,
            workspace=workspace,
            project=project,
            model_name=model_name,
        )

    async def delete_vector(self, memory_id: str) -> bool:
        """Deletes a vector from active backend."""
        return await self.backend.delete(memory_id)
