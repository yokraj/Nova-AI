"""Security Exception Hierarchy Module.

Defines custom security exception classes for audit failures, rate-limiting violations,
threat detection alerts, session expiration, WebSocket abuse, and compliance errors.
"""


class SecurityException(Exception):
    """Base exception class for all Security & Hardening failures."""

    def __init__(self, message: str = "Security exception occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class AuditException(SecurityException):
    """Raised when structured audit log generation or storage fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Audit logging error: {detail}")


class RateLimitException(SecurityException):
    """Raised when client exceeds allowed API or WebSocket request rate limits."""

    def __init__(self, key: str, rate: float, limit: int) -> None:
        super().__init__(f"Rate limit exceeded for '{key}': current rate {rate:.2f} req/min (limit {limit})")


class ThreatDetectedException(SecurityException):
    """Raised when a security threat event (brute-force, flooding, spam) is triggered."""

    def __init__(self, threat_type: str, detail: str) -> None:
        super().__init__(f"Security threat detected [{threat_type}]: {detail}")


class SessionExpiredException(SecurityException):
    """Raised when a user session token has expired or been terminated."""

    def __init__(self, session_id: str) -> None:
        super().__init__(f"Session '{session_id}' has expired or been revoked.")


class WebSocketSecurityException(SecurityException):
    """Raised when WebSocket message size limits or flood thresholds are breached."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"WebSocket security violation: {detail}")


class ComplianceException(SecurityException):
    """Raised when compliance report generation or audit verification fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Compliance error: {detail}")
