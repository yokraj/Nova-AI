"""Exceptions specific to the Agent SDK Execution Framework.
"""

from app.ai.shared import AIException


class ExecutionError(AIException):
    """Base exception for all execution framework errors."""

    pass


class RetryExceededError(ExecutionError):
    """Raised when job retry count limits are exceeded."""

    pass


class TimeoutError(ExecutionError):
    """Raised when execution task times out."""

    pass


class CancelledExecutionError(ExecutionError):
    """Raised when execution has been aborted/cancelled."""

    pass


class PipelineError(ExecutionError):
    """Raised when pipeline execution steps fail."""

    pass
