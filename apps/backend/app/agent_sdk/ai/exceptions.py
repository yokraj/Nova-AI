"""Exceptions specific to the Agent SDK AI Helper Library.
"""

from app.ai.shared import AIException


class AIHelperError(AIException):
    """Base exception for all AI Helper library operations."""

    pass


class ModelUnavailableError(AIHelperError):
    """Raised when the requested AI model or provider is not available."""

    pass


class StreamingError(AIHelperError):
    """Raised when streaming tokens generation fails."""

    pass


class EmbeddingError(AIHelperError):
    """Raised when text embeddings generation fails."""

    pass


class VisionError(AIHelperError):
    """Raised when vision model analysis operations fail."""

    pass
