"""Custom exceptions for the Enterprise AI Gateway.
"""

from app.ai.shared import AIException


class ProviderUnavailableError(AIException):
    """Raised when an AI provider is unreachable or unhealthy."""

    pass


class ProviderNotFoundError(AIException):
    """Raised when the requested provider name is not registered."""

    pass


class ModelUnavailableError(AIException):
    """Raised when the selected model key is not registered or supported."""

    pass


class CapabilityUnavailableError(AIException):
    """Raised when the capability interface is not supported."""

    pass


class GatewayTimeoutError(AIException):
    """Raised when gateway processing exceeds timeout limits."""

    pass


class GatewayConfigurationError(AIException):
    """Raised when the gateway configuration is invalid."""

    pass
