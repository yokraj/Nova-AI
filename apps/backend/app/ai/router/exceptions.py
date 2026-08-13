"""Custom exceptions for the Intelligent AI Model Router.
"""

from app.ai.exceptions import AiGatewayException

class ModelRoutingError(AiGatewayException):
    """Base exception class for all model routing errors."""
    pass

class ModelUnavailableError(ModelRoutingError):
    """Raised when the selected model is not registered or loaded in memory."""
    pass

class NoSuitableModelError(ModelRoutingError):
    """Raised when no registered model meets task capability requirements."""
    pass

class FallbackExhaustedError(ModelRoutingError):
    """Raised when all fallback models in the routing chain fail execution."""
    pass

class ResourceLimitError(ModelRoutingError):
    """Raised when a model is rejected due to local memory/VRAM constraints."""
    pass
