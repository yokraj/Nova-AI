"""Exceptions specific to the Agent SDK Observability SDK.
"""

from app.ai.shared import AIException


class ObservabilityError(AIException):
    """Base exception for all observability SDK errors."""

    pass


class TracingError(ObservabilityError):
    """Raised when trace or span operations fail."""

    pass


class MetricsError(ObservabilityError):
    """Raised when metrics collection fails."""

    pass


class TelemetryError(ObservabilityError):
    """Raised when telemetry collection or export fails."""

    pass


class AuditError(ObservabilityError):
    """Raised when audit log operations fail."""

    pass
