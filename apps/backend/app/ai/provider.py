"""Abstract Base Provider interface for Nova AI Gateway.

Declares methods and properties that all custom LLM provider implementations
must fulfill (e.g. text generation, chunk streaming, and capability checks).
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator

from app.ai.models import GenerationRequest, GenerationResponse, StreamChunk


class BaseProvider(ABC):
    """Abstract base class establishing the contract for custom AI providers."""

    @abstractmethod
    def get_name(self) -> str:
        """Returns the identifier name of the provider.

        Returns:
            The string identifier of the provider.
        """
        pass

    @abstractmethod
    async def generate_text(
        self, request: GenerationRequest
    ) -> GenerationResponse:
        """Processes a standard non-streaming text generation request.

        Args:
            request: The generation configuration and messages context.

        Returns:
            The completed GenerationResponse model mapping.

        Raises:
            AiGatewayException: If a provider or communication error occurs.
        """
        pass

    @abstractmethod
    async def generate_stream(
        self, request: GenerationRequest
    ) -> AsyncGenerator[StreamChunk, None]:
        """Processes a streaming text generation request.

        Args:
            request: The generation configuration and messages context.

        Yields:
            Incremental StreamChunk deltas.

        Raises:
            AiGatewayException: If a provider or communication error occurs.
        """
        # Yield is required to satisfy async generator syntax check
        yield  # type: ignore

    @abstractmethod
    def supports_model(self, model: str) -> bool:
        """Checks if the provider supports the requested model.

        Args:
            model: The name of the target model.

        Returns:
            True if supported; False otherwise.
        """
        pass

    @abstractmethod
    def supports_capability(self, capability: str) -> bool:
        """Checks if the provider supports a specific capability.

        Args:
            capability: The capability string (e.g. "vision", "embeddings").

        Returns:
            True if supported; False otherwise.
        """
        pass
