"""AI Gateway abstractions, policies, registries, and core orchestrator.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator

from app.ai.models import (
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderCapability,
    StreamingChunk,
)

# Legacy Service
from app.ai.gateway.service import AiGatewayService

# Interfaces
class IProviderFactory(ABC):
    """Abstract interface for constructing and validating AI providers."""

    @abstractmethod
    def create_provider(self, name: str, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def validate_provider(self, provider: Any, capability: ProviderCapability) -> bool:
        pass


class IAIGateway(ABC):
    """Abstract interface contract for central AI Gateway operations."""

    @abstractmethod
    async def chat(self, request: ChatRequest, **kwargs: Any) -> ChatResponse:
        pass

    @abstractmethod
    async def stream_chat(
        self, request: ChatRequest, **kwargs: Any
    ) -> AsyncGenerator[StreamingChunk, None]:
        yield StreamingChunk(content="")

    @abstractmethod
    async def embeddings(self, request: EmbeddingRequest, **kwargs: Any) -> EmbeddingResponse:
        pass

    @abstractmethod
    async def image_generation(self, prompt: str, model: str, **kwargs: Any) -> str:
        pass

    @abstractmethod
    async def speech(self, text: str, model: str, **kwargs: Any) -> bytes:
        pass

    @abstractmethod
    async def vision(self, image_path: str, prompt: str, model: str, **kwargs: Any) -> str:
        pass


# Concrete V2 Gateway Components
from app.ai.gateway.exceptions import (
    ProviderUnavailableError,
    ProviderNotFoundError,
    ModelUnavailableError,
    CapabilityUnavailableError,
    GatewayTimeoutError,
    GatewayConfigurationError,
)
from app.ai.gateway.gateway_config import GatewayConfig
from app.ai.gateway.request_context import RequestContext
from app.ai.gateway.response import GatewayResponse
from app.ai.gateway.retry_policy import RetryPolicy
from app.ai.gateway.timeout_policy import TimeoutPolicy
from app.ai.gateway.model_registry import ModelRegistry
from app.ai.gateway.provider_registry import ProviderRegistry
from app.ai.gateway.provider_factory import ProviderFactory
from app.ai.gateway.ai_gateway import AIGateway

__all__ = [
    "IProviderFactory",
    "IAIGateway",
    "AiGatewayService",
    "ProviderUnavailableError",
    "ProviderNotFoundError",
    "ModelUnavailableError",
    "CapabilityUnavailableError",
    "GatewayTimeoutError",
    "GatewayConfigurationError",
    "GatewayConfig",
    "RequestContext",
    "GatewayResponse",
    "RetryPolicy",
    "TimeoutPolicy",
    "ModelRegistry",
    "ProviderRegistry",
    "ProviderFactory",
    "AIGateway",
]
