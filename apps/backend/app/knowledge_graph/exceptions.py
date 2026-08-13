"""Knowledge Graph Exception Hierarchy Module.

Defines domain-specific exception types for Nova AI Enterprise Knowledge Graph Engine.
"""

from typing import Any, Dict, Optional


class KnowledgeGraphError(Exception):
    """Base exception class for all Knowledge Graph errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class EntityNotFoundError(KnowledgeGraphError):
    """Raised when requested graph entity node is not found."""
    pass


class RelationshipNotFoundError(KnowledgeGraphError):
    """Raised when requested graph relationship edge is not found."""
    pass


class GraphTraversalError(KnowledgeGraphError):
    """Raised when graph path traversal, BFS/DFS, or shortest path calculation fails."""
    pass


class EntityResolutionError(KnowledgeGraphError):
    """Raised when entity deduplication or alias resolution fails."""
    pass


class GraphHealthError(KnowledgeGraphError):
    """Raised when graph diagnostic health checks fail."""
    pass
