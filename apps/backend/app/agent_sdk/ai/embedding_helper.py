"""EmbeddingHelper wrapping vector generation placeholders and computations.
"""

import math
from typing import List, Optional

from app.ai.gateway.ai_gateway import AIGateway
from app.agent_sdk.ai.exceptions import EmbeddingError


class EmbeddingHelper:
    """Helper class for text embeddings generation and vector calculations."""

    def __init__(self, gateway: AIGateway) -> None:
        """Initializes EmbeddingHelper.

        Args:
            gateway: Active AIGateway instance.
        """
        self.gateway = gateway

    async def embed(self, text: str, model: Optional[str] = None) -> List[float]:
        """Generates embedding vector for a single text input string.

        Args:
            text: Input string query.
            model: Optional model override.

        Returns:
            List of float vector values.

        Raises:
            EmbeddingError: If generation fails or text is empty.
        """
        # TODO: Integrate with AI Gateway when embedding routes are supported.
        if not text:
            raise EmbeddingError("Input text cannot be empty.")
        return [0.1, 0.2, 0.3, 0.4, 0.5]

    async def embed_documents(self, documents: List[str], model: Optional[str] = None) -> List[List[float]]:
        """Generates embedding vectors for a list of document strings.

        Args:
            documents: List of input document strings.
            model: Optional model override.

        Returns:
            List of float vector lists.
        """
        # TODO: Integrate with AI Gateway when embedding routes are supported.
        return [await self.embed(doc, model=model) for doc in documents]

    async def similarity(self, text1: str, text2: str, model: Optional[str] = None) -> float:
        """Calculates similarity score between two texts.

        Args:
            text1: First input string.
            text2: Second input string.
            model: Optional model override.

        Returns:
            Float similarity score.
        """
        # TODO: Integrate with AI Gateway when embedding routes are supported.
        vec1 = await self.embed(text1, model=model)
        vec2 = await self.embed(text2, model=model)
        return self.cosine_similarity(vec1, vec2)

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculates cosine similarity coefficient between two vectors.

        Args:
            vec1: First float vector.
            vec2: Second float vector.

        Returns:
            Cosine similarity score between -1.0 and 1.0.
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = math.sqrt(sum(a * a for a in vec1))
        norm_b = math.sqrt(sum(b * b for b in vec2))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)
