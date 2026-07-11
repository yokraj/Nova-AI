"""Exceptions specific to the System Event Bus subsystem.
"""

from app.ai.shared import AIException


class SystemEventError(AIException):
    """Base exception for all system event bus operations."""

    pass


class EventPublishError(SystemEventError):
    """Raised when publishing system events fails."""

    pass


class EventReplayError(SystemEventError):
    """Raised when replaying system events fails."""

    pass


class HandlerError(SystemEventError):
    """Raised when an event handler fails to process a system event."""

    pass
