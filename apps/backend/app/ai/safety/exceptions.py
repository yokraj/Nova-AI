"""Custom exceptions for the Human Approval & Safety Engine.
"""

class SafetyError(Exception):
    """Base exception for all safety and approval engine errors."""
    pass

class PermissionDenied(SafetyError):
    """Raised when an action is executed without required user approvals."""
    pass

class PolicyViolation(SafetyError):
    """Raised when a system security policy constraint is violated."""
    pass
