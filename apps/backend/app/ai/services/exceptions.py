"""Typed exception hierarchy for Autonomous Internet & Service Automation."""


class ServiceAutomationError(Exception):
    """Base exception for service automation platform errors."""
    pass


class WorkflowExecutionError(ServiceAutomationError):
    """Raised when a service workflow execution fails."""
    pass


class AuthenticationFailedError(ServiceAutomationError):
    """Raised when website authentication fails."""
    pass


class CaptchaInterceptionError(ServiceAutomationError):
    """Raised when CAPTCHA challenge cannot be resolved."""
    pass


class PaymentGuardError(ServiceAutomationError):
    """Raised when a payment or financial transaction is rejected by safety guard or user."""
    pass


class OTPRequiredError(ServiceAutomationError):
    """Raised when 2FA / OTP verification is required."""
    pass


class ServiceNotFoundError(ServiceAutomationError):
    """Raised when a requested service ID or domain workflow is not found."""
    pass
