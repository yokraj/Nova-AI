"""Shared exceptions and utilities for the AI Platform.
"""

from typing import Any, List, Optional
from app.ai.models import AIModelInfo, ProviderCapability
from app.ai.providers.contracts import (
    IEmbeddingProvider,
    IImageProvider,
    ILLMProvider,
    ISpeechProvider,
    IVisionProvider,
)


# ====================================================
# Exceptions
# ====================================================
class AIException(Exception):
    """Base exception for all AI Platform errors."""

    pass


class ProviderUnavailable(AIException):
    """Raised when the AI provider is unreachable or reports unhealthy diagnostics."""

    pass


class ProviderNotFound(AIException):
    """Raised when the requested provider name is not registered."""

    pass


class ModelUnavailable(AIException):
    """Raised when the selected model identifier is not active."""

    pass


class CapabilityUnavailable(AIException):
    """Raised when the capability interface is not supported."""

    pass


class GatewayException(AIException):
    """Raised when gateway processing fails or times out."""

    pass


# ====================================================
# Shared Utilities
# ====================================================
class ProviderValidator:
    """Helper validator verifying provider interfaces implementation conformity."""

    @staticmethod
    def validate(provider: Any, capability: ProviderCapability) -> bool:
        """Verifies if provider implements abstract contracts matching capability.

        Args:
            provider: Concrete provider adapter.
            capability: Requested ProviderCapability.

        Returns:
            True if valid; False otherwise.
        """
        if capability == ProviderCapability.CHAT:
            return isinstance(provider, ILLMProvider)
        if capability == ProviderCapability.EMBEDDINGS:
            return isinstance(provider, IEmbeddingProvider)
        if capability == ProviderCapability.IMAGE:
            return isinstance(provider, IImageProvider)
        if capability == ProviderCapability.SPEECH:
            return isinstance(provider, ISpeechProvider)
        if capability == ProviderCapability.VISION:
            return isinstance(provider, IVisionProvider)
        return False


# Standardized lowercase utility naming as per prompt requirements
providerValidator = ProviderValidator()


class CapabilityResolver:
    """Helper resolving actions strings to ProviderCapability enums."""

    @staticmethod
    def map_action_to_capability(action: str) -> Optional[ProviderCapability]:
        """Maps an execution method name to capability requirements.

        Args:
            action: Method name (e.g. 'chat', 'embeddings').

        Returns:
            Matched ProviderCapability, or None.
        """
        cleaned = action.strip().lower()
        if cleaned in ("chat", "stream_chat", "generate_text", "generate_stream"):
            return ProviderCapability.CHAT
        if cleaned in ("embed", "embeddings", "embed_text", "embed_batch"):
            return ProviderCapability.EMBEDDINGS
        if cleaned in ("image", "image_generation", "generate_image", "edit_image"):
            return ProviderCapability.IMAGE
        if cleaned in ("speech", "speech_to_text", "text_to_speech"):
            return ProviderCapability.SPEECH
        if cleaned in ("vision", "analyze_image"):
            return ProviderCapability.VISION
        return None


class ModelSelector:
    """Helper selecting appropriate models matching capabilities."""

    @staticmethod
    def select_model(models: List[AIModelInfo], capability: ProviderCapability) -> Optional[str]:
        """Selects the first model supporting target capability.

        Args:
            models: List of available model info metadata.
            capability: Target capability enum.

        Returns:
            Best matched model name, or None.
        """
        for model in models:
            if capability in model.capabilities:
                return model.name
        return None
