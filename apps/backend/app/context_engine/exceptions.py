"""Context Engine Exception Hierarchy Module.

Defines domain-specific exception types for Nova AI Enterprise Context Engine.
"""

from typing import Any, Dict, Optional


class ContextEngineError(Exception):
    """Base exception class for all Context Engine errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ContextSelectionError(ContextEngineError):
    """Raised when context selection across sub-engines fails."""
    pass


class ContextFusionError(ContextEngineError):
    """Raised when weighted score fusion fails."""
    pass


class ConflictResolutionError(ContextEngineError):
    """Raised when conflict resolution fails to pick highest confidence info."""
    pass


class TokenBudgetExceededError(ContextEngineError):
    """Raised when context size exceeds maximum token budget window."""
    pass


class ContextCompressionError(ContextEngineError):
    """Raised when context compression fails."""
    pass


class ContextCacheError(ContextEngineError):
    """Raised when context cache lookup or eviction fails."""
    pass


class ContextHealthError(ContextEngineError):
    """Raised when context engine diagnostic health checks fail."""
    pass
