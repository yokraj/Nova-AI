"""RAG Exception Hierarchy Module.

Defines domain-specific exception types for Nova AI Hybrid RAG Engine.
"""

from typing import Any, Dict, Optional


class RAGError(Exception):
    """Base exception class for all Hybrid RAG errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class QueryAnalysisError(RAGError):
    """Raised when query analyzer fails to classify query intent."""
    pass


class QueryRewriteError(RAGError):
    """Raised when query rewriter fails during pronoun or context resolution."""
    pass


class RetrievalError(RAGError):
    """Raised when parallel keyword or semantic retrieval fails."""
    pass


class RerankingError(RAGError):
    """Raised when cross-encoder reranker fails during candidate scoring."""
    pass


class ContextOverflowError(RAGError):
    """Raised when assembled context exceeds total token budget."""
    pass


class GroundingValidationError(RAGError):
    """Raised when generated response fails factual grounding validation."""
    pass


class CitationError(RAGError):
    """Raised when citation generation fails to resolve source memory or document IDs."""
    pass
