"""Exceptions specific to the Nova Orchestrator subsystem.
"""

from app.ai.shared import AIException


class OrchestratorException(AIException):
    """Base exception for all Nova Orchestrator operations."""

    pass


class OrchestrationError(OrchestratorException):
    """Raised when orchestrator execution coordination fails."""

    pass


class PlanningError(OrchestratorException):
    """Raised when task planning or splitting/merging fails."""

    pass


class IntentClassificationError(OrchestratorException):
    """Raised when classifying prompt intent fails."""

    pass


class SelectionError(OrchestratorException):
    """Raised when agent selection or ranking fails."""

    pass


class ExecutionError(OrchestratorException):
    """Raised when task execution fails."""

    pass
