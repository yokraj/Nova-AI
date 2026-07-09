"""Custom exceptions and error normalization helpers for the Nova AI Gateway.

Provides structured exception classes mapping standard API, network,
or client-side validation errors.
"""

from typing import Any, Optional


class AiGatewayException(Exception):
    """Base exception for all AI Gateway errors."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.details = details


class ProviderTimeoutException(AiGatewayException):
    """Exception raised when an AI provider fails to respond in time."""

    pass


class ProviderRateLimitException(AiGatewayException):
    """Exception raised when an AI provider throttles request quotas."""

    pass


class InvalidModelException(AiGatewayException):
    """Exception raised when an invalid or unsupported model is requested."""

    pass


def normalize_provider_error(
    provider_name: str, error: Exception
) -> AiGatewayException:
    """Translates raw provider errors to standardized gateway exceptions.

    Args:
        provider_name: The name of the provider that threw the error.
        error: The raw Python exception instance caught.

    Returns:
        The normalized AiGatewayException instance.
    """
    import asyncio

    # Explicitly check for TimeoutError instances
    if isinstance(error, (asyncio.TimeoutError, TimeoutError)):
        return ProviderTimeoutException(
            message=f"Provider '{provider_name}' request timed out.",
            provider=provider_name,
            details=error,
        )

    error_message = str(error)

    # Detect timeout errors in case of string-based message lookups
    if "timeout" in error_message.lower() or "deadline exceeded" in error_message.lower():
        return ProviderTimeoutException(
            message=f"Provider '{provider_name}' request timed out.",
            provider=provider_name,
            details=error,
        )

    # Detect rate limiting errors
    if "rate limit" in error_message.lower() or "429" in error_message:
        return ProviderRateLimitException(
            message=f"Provider '{provider_name}' rate limit exceeded.",
            provider=provider_name,
            details=error,
        )

    # Default fallback
    return AiGatewayException(
        message=f"Provider '{provider_name}' query failed: {error_message}",
        provider=provider_name,
        details=error,
    )
