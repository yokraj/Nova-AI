"""Exceptions specific to the Agent Permission subsystem.
"""

from app.ai.shared import AIException


class AgentPermissionError(AIException):
    """Base exception for all agent permission manager operations."""

    pass


class PermissionDeniedError(AgentPermissionError):
    """Raised when access is denied by security policy rules."""

    pass


class PermissionExpiredError(AgentPermissionError):
    """Raised when a temporary permission has expired."""

    pass


class InvalidPermissionError(AgentPermissionError):
    """Raised when access is requested for an invalid or unsupported permission."""

    pass


class PolicyViolationError(AgentPermissionError):
    """Raised when action violates platform security policy guidelines."""

    pass
