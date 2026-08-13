"""Custom exception hierarchy for Computer Vision & Adaptive GUI Intelligence.
"""


class ComputerVisionError(Exception):
    """Base exception for all Computer Vision errors."""

    pass


class ScreenCaptureError(ComputerVisionError):
    """Raised when screen or window capture fails."""

    pass


class GUIElementNotFoundError(ComputerVisionError):
    """Raised when Adaptive UI Locator fails to find target control."""

    pass


class VisualReasoningFailedError(ComputerVisionError):
    """Raised when Visual Reasoning Engine fails to diagnose screen state."""

    pass


class OCRProcessingError(ComputerVisionError):
    """Raised when OCR or document understanding fails to extract text."""

    pass


class RecoveryFailedError(ComputerVisionError):
    """Raised when Adaptive Automation Recovery cannot resolve failure."""

    pass
