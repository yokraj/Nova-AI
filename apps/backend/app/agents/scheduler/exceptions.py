"""Exceptions specific to the Agent Scheduler subsystem.
"""

from app.ai.shared import AIException


class AgentSchedulerError(AIException):
    """Base exception for all agent scheduler operations."""

    pass


class JobNotFoundError(AgentSchedulerError):
    """Raised when a specified job is not found."""

    pass


class SchedulerError(AgentSchedulerError):
    """Raised when scheduler operations fail."""

    pass


class JobTimeoutError(AgentSchedulerError):
    """Raised when a job execution exceeds its configured timeout duration."""

    pass


class RetryLimitExceededError(AgentSchedulerError):
    """Raised when a job exceeds its maximum permitted retry attempts."""

    pass
