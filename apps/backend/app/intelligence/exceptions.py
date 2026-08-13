"""Intelligence Engine Exception Hierarchy Module.

Defines domain-specific exception types for Nova AI Universal Intelligence Engine.
"""

from typing import Any, Dict, Optional


class IntelligenceError(Exception):
    """Base exception class for all Universal Intelligence Engine errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ModelRoutingError(IntelligenceError):
    """Raised when model router fails to select or communicate with target LLM provider."""
    pass


class PlanningError(IntelligenceError):
    """Raised when task planner fails to decompose goal or generate execution graph."""
    pass


class ReasoningError(IntelligenceError):
    """Raised when reasoning engine encounters logical inconsistencies or failures."""
    pass


class KnowledgeRetrievalError(IntelligenceError):
    """Raised when RAG or document knowledge engine fails during search or synthesis."""
    pass


class ToolRoutingError(IntelligenceError):
    """Raised when tool router fails to resolve or execute target tool."""
    pass


class AgentRoutingError(IntelligenceError):
    """Raised when agent router fails to assign specialized workforce agent."""
    pass


class VerificationError(IntelligenceError):
    """Raised when verification engine detects hallucinations or invalid code/logic."""
    pass


class ReflectionError(IntelligenceError):
    """Raised when reflection engine fails during self-critique loop."""
    pass


class ContextCompressionError(IntelligenceError):
    """Raised when context manager fails to compress or truncate conversation history."""
    pass


class LearningAdaptationError(IntelligenceError):
    """Raised when learning engine fails to persist or retrieve user preference profiles."""
    pass


class IntentDetectionError(IntelligenceError):
    """Raised when intent detector fails to classify or extract parameters from input."""
    pass
