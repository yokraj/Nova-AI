"""Security custom exceptions for Nova AI Identity Platform.

Provides structured error mappings for failed logins, expired tokens,
and refresh tokens reuse attempts.
"""

from app.runtime.exceptions import KernelException


class SecurityException(KernelException):
    """Base exception for all identity security errors."""

    pass


class InvalidCredentialsError(SecurityException):
    """Exception raised when credentials verification checks fail."""

    pass


class InvalidTokenError(SecurityException):
    """Exception raised when token decoding or signature validation fails."""

    pass


class ExpiredTokenError(InvalidTokenError):
    """Exception raised when token lifetime expiration check fails."""

    pass


class TokenReuseDetectedError(SecurityException):
    """Exception raised when an invalid/revoked refresh token is re-presented."""

    pass
