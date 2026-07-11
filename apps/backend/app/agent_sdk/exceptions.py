"""Exceptions specific to the Agent SDK Foundation.
"""

from app.ai.shared import AIException


class SDKException(AIException):
    """Base exception for all agent SDK operations."""

    pass


class SDKInitializationError(SDKException):
    """Raised when SDK initialization fails."""

    pass


class SDKConfigurationError(SDKException):
    """Raised when SDK configuration loading or validation fails."""

    pass


class SDKRuntimeError(SDKException):
    """Raised when a runtime error occurs within the agent SDK execution context."""

    pass
