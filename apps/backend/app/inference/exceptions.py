"""Inference Gateway Exception Hierarchy Module.

Defines domain-specific exception types for Nova AI Enterprise Inference Gateway.
"""

from typing import Any, Dict, Optional


class InferenceEngineError(Exception):
    """Base exception class for all Inference Gateway errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ProviderUnavailableError(InferenceEngineError):
    """Raised when an LLM provider (Ollama, vLLM, OpenAI) is unreachable or unhealthy."""
    pass


class ModelNotFoundError(InferenceEngineError):
    """Raised when target model is not registered or supported."""
    pass


class GPUSchedulingError(InferenceEngineError):
    """Raised when GPU memory allocation or VRAM reservation fails."""
    pass


class ContextOverflowError(InferenceEngineError):
    """Raised when prompt context exceeds model maximum context window."""
    pass


class CircuitBreakerOpenError(InferenceEngineError):
    """Raised when circuit breaker is open due to repeated provider failures."""
    pass


class StreamingError(InferenceEngineError):
    """Raised when SSE or token streaming disconnects unexpectedly."""
    pass
