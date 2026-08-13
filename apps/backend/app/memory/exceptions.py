"""Memory Exceptions Module.

Defines domain-specific exception types for Nova AI Enterprise Memory Foundation.
"""

from typing import Any, Dict, Optional


class MemoryError(Exception):
    """Base exception for all memory foundation errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class MemoryNotFoundError(MemoryError):
    """Raised when target memory entry or entity is not found."""
    pass


class MemoryValidationError(MemoryError):
    """Raised when memory creation or update schema validation fails."""
    pass


class MemoryRelationshipError(MemoryError):
    """Raised when linking or creating memory relationships encounters invalid references."""
    pass


class MemoryStorageError(MemoryError):
    """Raised when memory repository persistence operations fail."""
    pass


class MemoryCompressionError(MemoryError):
    """Raised when memory compression engine fails during thread summarization."""
    pass


class MemoryAccessDeniedError(MemoryError):
    """Raised when RBAC or workspace isolation checks prevent memory access."""
    pass
