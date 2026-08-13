"""Vector Memory Exception Hierarchy Module.

Defines domain-specific exception types for Nova AI Vector Database & Embedding Engine.
"""

from typing import Any, Dict, Optional


class VectorError(Exception):
    """Base exception class for all vector memory errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class EmbeddingGenerationError(VectorError):
    """Raised when local or remote embedding model generation fails."""
    pass


class VectorDimensionMismatchError(VectorError):
    """Raised when input vector dimension does not match index dimension."""
    pass


class VectorStoreError(VectorError):
    """Raised when vector store persistence or index operation fails."""
    pass


class VectorIndexNotFoundError(VectorError):
    """Raised when requested vector index or partition is not found."""
    pass


class VectorCacheError(VectorError):
    """Raised when vector cache lookup or eviction fails."""
    pass


class VectorHealthError(VectorError):
    """Raised when vector engine health diagnostics check fails."""
    pass
