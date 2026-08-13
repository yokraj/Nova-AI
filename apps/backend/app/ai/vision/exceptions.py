"""Custom exceptions for the Enterprise Vision & Computer Interaction Engine.
"""

from app.ai.exceptions import AiGatewayException

class VisionEngineError(AiGatewayException):
    """Base exception for all vision engine errors."""
    pass

class ImageProcessingError(VisionEngineError):
    """Raised when an error occurs during image pre-processing or loading."""
    pass

class ScreenshotCaptureError(VisionEngineError):
    """Raised when screenshot capturing fails."""
    pass

class OCRError(VisionEngineError):
    """Raised when optical character recognition text extraction fails."""
    pass

class UIElementDetectionError(VisionEngineError):
    """Raised when UI controls or elements cannot be identified."""
    pass

class ActionPlanningError(VisionEngineError):
    """Raised when constructing action plan steps fails."""
    pass
