"""Retry policy configuration for handling transient AI provider failures.
"""

import asyncio
from typing import List, Optional, Type


class RetryPolicy:
    """Configures retry execution thresholds and backoff multipliers."""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
        retryable_exceptions: Optional[List[Type[Exception]]] = None,
    ) -> None:
        """Initializes RetryPolicy.

        Args:
            max_retries: Maximum number of retry attempts.
            backoff_factor: Multiplier for exponential backoff duration.
            retryable_exceptions: List of exception classes that trigger retries.
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retryable_exceptions = retryable_exceptions or [
            asyncio.TimeoutError,
            ConnectionError,
        ]

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Checks if a failure qualifies for another retry check.

        Args:
            exception: Exception that was raised.
            attempt: Number of attempts completed so far.

        Returns:
            True if retry limit is not exceeded and exception type matches.
        """
        if attempt >= self.max_retries:
            return False
        return any(isinstance(exception, t) for t in self.retryable_exceptions)
