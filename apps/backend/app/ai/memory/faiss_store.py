"""FAISS Local Fallback Vector Store adapter.
"""

import os
import json
from typing import List, Dict, Any
from uuid import UUID
import math
from app.ai.memory.vector_store import IVectorStore
from app.ai.memory.models import MemoryItem, RetrievalResult, MemoryType

class FAISSVectorStore(IVectorStore):
    """Memory-only and file-serialized vector store acting as a local FAISS fallback database."""

    def __init__(self, storage_path: str = ".nova/memory/") -> None:
        self.storage_path = storage_path
        self.index_file = os.path.join(storage_path, "faiss_index.json")
        self.items: Dict[str, MemoryItem] = {}
        self.load()

    def load(self) -> None:
        """Loads serialized indices from disk cache."""
        if not os.path.exists(self.index_file):
            return
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    self.items[k] = MemoryItem(
                        id=UUID(v["id"]),
                        content=v["content"],
                        memory_type=MemoryType(v["memory_type"]),
                        metadata=v["metadata"],
                        embedding=v["embedding"],
                        importance_score=v.get("importance_score", 0.5)
                    )
        except Exception:
            pass

    def save(self) -> None:
        """Serializes current index nodes to file."""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            data = {}
            for k, v in self.items.items():
                data[k] = {
                    "id": str(v.id),
                    "content": v.content,
                    "memory_type": v.memory_type.value,
                    "metadata": v.metadata,
                    "embedding": v.embedding,
                    "importance_score": v.importance_score
                }
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    async def add(self, items: List[MemoryItem]) -> None:
        """Stores memory nodes locally."""
        for item in items:
            self.items[str(item.id)] = item
        self.save()

    async def search(self, query_vector: List[float], limit: int = 5, threshold: float = 0.7) -> List[RetrievalResult]:
        """Performs local cosine similarity calculations."""
        results = []
        for item_id, item in self.items.items():
            if not item.embedding:
                continue

            # Cosine similarity
            dot_product = sum(a * b for a, b in zip(query_vector, item.embedding))
            norm_a = math.sqrt(sum(a * a for a in query_vector))
            norm_b = math.sqrt(sum(b * b for b in item.embedding))

            if norm_a == 0 or norm_b == 0:
                similarity = 0.0
            else:
                similarity = dot_product / (norm_a * norm_b)

            if similarity >= threshold:
                results.append(
                    RetrievalResult(
                        memory_id=item.id,
                        content=item.content,
                        similarity_score=similarity,
                        source=item.metadata.get("source", "local"),
                        metadata=item.metadata
                    )
                )

        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:limit]

    async def delete(self, item_id: UUID) -> None:
        """Removes memory item from index."""
        str_id = str(item_id)
        if str_id in self.items:
            del self.items[str_id]
            self.save()

    async def update(self, item: MemoryItem) -> None:
        """Updates index node attributes."""
        self.items[str(item.id)] = item
        self.save()

    async def count(self) -> int:
        """Returns node count."""
        return len(self.items)
