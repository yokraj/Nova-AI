"""Interface definition for vector stores.
"""

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from app.ai.memory.models import MemoryItem, RetrievalResult

class IVectorStore(ABC):
    """Abstract interface for vector search databases."""

    @abstractmethod
    async def add(self, items: List[MemoryItem]) -> None:
        """Stores new memory nodes and their vector representations."""
        pass

    @abstractmethod
    async def search(self, query_vector: List[float], limit: int = 5, threshold: float = 0.7) -> List[RetrievalResult]:
        """Performs cosine similarity search against index."""
        pass

    @abstractmethod
    async def delete(self, item_id: UUID) -> None:
        """Deletes item by primary ID."""
        pass

    @abstractmethod
    async def update(self, item: MemoryItem) -> None:
        """Updates content or metadata attributes of a memory item."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Returns the total number of index nodes."""
        pass
