"""Custom exception hierarchy for the Nova AI Runtime Kernel.

Provides structured errors mapping system boot failures, capability lifecycles,
service registration conflicts, and resource limit exhausts.
"""

from typing import Any, Optional


class KernelException(Exception):
    """Base exception for all Nova OS Runtime Kernel errors."""

    def __init__(
        self, message: str, details: Optional[Any] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class CapabilityException(KernelException):
    """Exception raised during capability validation or lifecycle execution."""

    pass


class ServiceRegistrationException(KernelException):
    """Exception raised on service collision or unresolved dependency injections."""

    pass


class ResourceExhaustedException(KernelException):
    """Exception raised when resource allocation limits are breached."""

    pass
