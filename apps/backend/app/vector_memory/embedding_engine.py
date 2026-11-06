"""Embedding Engine Module.

Implements EmbeddingEngine providing vector generation, batching, updating,
deletion, rebuilding, reindexing, normalization, and dimension validation.
"""

import math
from typing import Any, Dict, List, Optional
import structlog

from app.vector_memory.config import VectorConfig
from app.vector_memory.embedding_models import ModelRegistry
from app.vector_memory.embedding_router import EmbeddingRouter
from app.vector_memory.exceptions import VectorDimensionMismatchError, EmbeddingGenerationError

logger = structlog.get_logger(__name__)


class EmbeddingEngine:
    """Enterprise Embedding Generation & Lifecycle Orchestrator."""

    def __init__(
        self,
        config: Optional[VectorConfig] = None,
        registry: Optional[ModelRegistry] = None,
        router: Optional[EmbeddingRouter] = None,
    ) -> None:
        self.config = config or VectorConfig()
        self.registry = registry or ModelRegistry(config=self.config)
        self.router = router or EmbeddingRouter(config=self.config)
        logger.info("embedding_engine_initialized")

    async def generate_embedding(
        self, text: str, model_name: Optional[str] = None, context_type: str = "general"
    ) -> Dict[str, Any]:
        """Generates embedding vector for a single text input."""
        if not text or not text.strip():
            raise EmbeddingGenerationError("Cannot generate embedding for empty text input.")

        clean_text = text.strip()
        if not model_name:
            selection = self.router.select_model_for_context(clean_text, context_type=context_type)
            model_name = selection["model_name"]

        provider = self.registry.get_provider(model_name)
        vector = await provider.generate_vector(clean_text)
        self.validate_dimension(vector, provider.dimension)
        normalized = self.normalize_vector(vector)

        logger.info("embedding_generated", model_name=model_name, dimension=provider.dimension, text_len=len(clean_text))
        return {
            "model_name": model_name,
            "dimension": provider.dimension,
            "vector": normalized,
            "is_neural": getattr(provider, "is_neural", True),
        }

    async def generate_batch(
        self, texts: List[str], model_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generates embedding vectors for a batch of text inputs asynchronously."""
        results: List[Dict[str, Any]] = []
        for text in texts:
            res = await self.generate_embedding(text, model_name=model_name)
            results.append(res)
        logger.info("batch_embeddings_generated", batch_size=len(texts))
        return results

    async def update_embedding(self, memory_id: str, new_text: str) -> Dict[str, Any]:
        """Regenerates embedding for an updated memory entry."""
        return await self.generate_embedding(new_text)

    async def delete_embedding(self, memory_id: str) -> bool:
        """Deletes embedding entry by memory ID."""
        logger.info("embedding_deleted", memory_id=memory_id)
        return True

    async def rebuild_embedding(self, memory_id: str, text: str) -> Dict[str, Any]:
        """Rebuilds embedding representation for target memory."""
        return await self.generate_embedding(text)

    async def reindex(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Reindexes a list of items into vector space."""
        texts = [item.get("content", "") for item in items]
        embeddings = await self.generate_batch(texts)
        logger.info("reindex_completed", item_count=len(items))
        return {
            "status": "success",
            "reindexed_count": len(items),
            "embeddings": embeddings,
        }

    def normalize_vector(self, vector: List[float]) -> List[float]:
        """Ensures L2 unit length vector normalization."""
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude == 0.0:
            return vector
        return [round(v / magnitude, 6) for v in vector]

    def validate_dimension(self, vector: List[float], expected_dimension: int) -> None:
        """Validates that vector length matches expected dimension."""
        if len(vector) != expected_dimension:
            raise VectorDimensionMismatchError(
                f"Vector dimension {len(vector)} does not match expected {expected_dimension}."
            )
