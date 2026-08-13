"""Custom exception hierarchy for Universal Desktop, Browser & OS Automation Engine.
"""


class DesktopAutomationError(Exception):
    """Base exception for all Desktop Automation Engine errors."""

    pass


class WindowNotFoundError(DesktopAutomationError):
    """Raised when target window is not found on screen."""

    pass


class ControlNotFoundError(DesktopAutomationError):
    """Raised when target GUI control element cannot be resolved by Accessibility, Vision, or OCR."""

    pass


class VerificationFailedError(DesktopAutomationError):
    """Raised when action verification step fails."""

    pass


class ApprovalRequiredError(DesktopAutomationError):
    """Raised when a sensitive or destructive action requires explicit human approval hold."""

    pass
