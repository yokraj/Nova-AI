"""Exceptions specific to the Agent Registry subsystem.
"""

from app.ai.shared import AIException


class AgentRegistryError(AIException):
    """Base exception for all agent registry operations."""

    pass


class DuplicateAgentError(AgentRegistryError):
    """Raised when registering an agent with an already-registered identifier or name."""

    pass


# For backwards compatibility with existing codebase
AgentDuplicateError = DuplicateAgentError


class AgentNotFoundError(AgentRegistryError):
    """Raised when a requested agent metadata descriptor is missing."""

    pass


class AgentInitializationError(AgentRegistryError):
    """Raised when initializing an agent instance fails."""

    pass


class AgentRegistrationError(AgentRegistryError):
    """Raised when registering an agent fails."""

    pass

