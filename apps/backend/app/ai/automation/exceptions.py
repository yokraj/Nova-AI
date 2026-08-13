"""Typed exception hierarchy for the Native Desktop & Browser Automation Engine."""


class AutomationError(Exception):
    """Base exception for all automation engine errors."""
    pass


class DesktopError(AutomationError):
    """Raised when desktop OS automation fails."""
    pass


class BrowserError(AutomationError):
    """Raised when browser automation fails."""
    pass


class WindowNotFoundError(AutomationError):
    """Raised when a specified window handle or title cannot be located."""
    pass


class ElementNotFoundError(AutomationError):
    """Raised when a UI element or CSS/XPath selector cannot be located."""
    pass


class OCRProcessingError(AutomationError):
    """Raised when OCR text extraction fails."""
    pass


class AutomationSafetyError(AutomationError):
    """Raised when an automation action is blocked due to safety violations."""
    pass
