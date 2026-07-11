"""Exceptions specific to the Ollama provider.
"""

from app.ai.shared import AIException


class OllamaProviderError(AIException):
    """Base exception for all Ollama provider errors."""

    pass


class OllamaConnectionError(OllamaProviderError):
    """Raised when connecting to Ollama server fails."""

    pass


class OllamaTimeoutError(OllamaProviderError):
    """Raised when an operation times out."""

    pass


class OllamaModelNotFoundError(OllamaProviderError):
    """Raised when the requested model is not found on the Ollama server."""

    pass
