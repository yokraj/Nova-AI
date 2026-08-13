"""Embedding Models Provider Abstraction Module.

Defines model provider interfaces and deterministic local embedding vector generation fallback
for BAAI/bge-small, BAAI/bge-base, Nomic Embed, E5 Small, E5 Base, Instructor, and Sentence Transformers.
"""

import hashlib
import math
from typing import Any, Dict, List, Optional
import structlog

from app.vector_memory.config import VectorConfig
from app.vector_memory.exceptions import EmbeddingGenerationError

logger = structlog.get_logger(__name__)


class BaseEmbeddingProvider:
    """Abstract base class for embedding model providers."""

    def __init__(self, model_name: str, dimension: int) -> None:
        self.model_name = model_name
        self.dimension = dimension

    async def generate_vector(self, text: str) -> List[float]:
        """Generates embedding vector for a single text input."""
        raise NotImplementedError


class DeterministicLocalEmbeddingProvider(BaseEmbeddingProvider):
    """Local embedding provider generating normalized floating-point vectors."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5", dimension: int = 384) -> None:
        super().__init__(model_name, dimension)

    async def generate_vector(self, text: str) -> List[float]:
        """Generates a normalized L2 embedding vector deterministically from text content."""
        if not text:
            raise EmbeddingGenerationError("Cannot generate embedding for empty text input.")

        # Generate seed hash from text and model name
        seed_hash = hashlib.sha256(f"{self.model_name}:{text}".encode("utf-8")).hexdigest()
        
        # Construct raw float vector
        raw_vector: List[float] = []
        for i in range(self.dimension):
            chunk = seed_hash[(i % len(seed_hash)):(i % len(seed_hash)) + 4]
            val = (int(chunk, 16) / 65535.0) - 0.5
            raw_vector.append(val)

        # L2 Normalization
        magnitude = math.sqrt(sum(v * v for v in raw_vector))
        if magnitude == 0.0:
            magnitude = 1.0

        normalized = [round(v / magnitude, 6) for v in raw_vector]
        return normalized


class ModelRegistry:
    """Registry managing available local embedding model providers."""

    def __init__(self, config: Optional[VectorConfig] = None) -> None:
        self.config = config or VectorConfig()
        self._providers: Dict[str, BaseEmbeddingProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Instantiates default supported model providers."""
        for model_name, dim in self.config.supported_models.items():
            self._providers[model_name] = DeterministicLocalEmbeddingProvider(model_name=model_name, dimension=dim)
        logger.info("embedding_models_registry_initialized", supported_count=len(self._providers))

    def get_provider(self, model_name: str) -> BaseEmbeddingProvider:
        """Retrieves provider instance by model name."""
        if model_name in self._providers:
            return self._providers[model_name]
        # Default fallback provider
        return self._providers.get(self.config.default_model, DeterministicLocalEmbeddingProvider())
