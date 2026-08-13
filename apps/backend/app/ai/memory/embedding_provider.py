"""Interface definition for embedding providers.
"""

from abc import ABC, abstractmethod
from typing import List

class IEmbeddingProvider(ABC):
    """Abstract interface for text embeddings generations."""

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generates embedding vector for a single text segment."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for multiple text segments in batch."""
        pass
