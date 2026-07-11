"""Exceptions specific to the Agent Communication Bus subsystem.
"""

from app.ai.shared import AIException


class AgentBusError(AIException):
    """Base exception for all agent communication bus operations."""

    pass


class RoutingError(AgentBusError):
    """Raised when request/message routing fails."""

    pass


class MessageValidationError(AgentBusError):
    """Raised when message content validation fails."""

    pass


class SubscriptionError(AgentBusError):
    """Raised when event subscriptions fail."""

    pass
