"""RetryEngine managing exponential backoff pause steps.
"""

import asyncio
from typing import Any, Callable, Coroutine, List, Optional, Type

from app.agent_sdk.execution.exceptions import RetryExceededError


class RetryEngine:
    """Engine executing retries with exponential backoffs."""

    def __init__(
        self,
        max_attempts: int = 3,
        backoff_factor: float = 2.0,
        initial_delay: float = 1.0,
        retryable_exceptions: Optional[List[Type[BaseException]]] = None,
    ) -> None:
        """Initializes RetryEngine.

        Args:
            max_attempts: Maximum retry count budget.
            backoff_factor: Multiplier for exponential backoff calculations.
            initial_delay: Initial pause duration in seconds.
            retryable_exceptions: List of exception types triggers.
        """
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
        self.initial_delay = initial_delay
        self.retryable_exceptions = retryable_exceptions or [Exception]

    def fixed_delay(self) -> float:
        """Returns constant delay duration.

        Returns:
            Fixed delay in seconds.
        """
        return self.initial_delay

    def exponential_backoff(self, attempt: int) -> float:
        """Calculates backoff pause duration for attempt.

        Args:
            attempt: Index of retry attempt (1-indexed).

        Returns:
            Exponential backoff delay in seconds.
        """
        return self.initial_delay * (self.backoff_factor ** (attempt - 1))

    async def execute(
        self, coro_func: Callable[..., Coroutine[Any, Any, Any]], *args: Any, **kwargs: Any
    ) -> Any:
        """Executes a coroutine function retrying on exceptions.

        Args:
            coro_func: Coroutine callable.
            args: Target function positional arguments.
            kwargs: Target function keyword arguments.

        Returns:
            Coroutine output value.

        Raises:
            RetryExceededError: If max attempts limit is breached.
        """
        last_error = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return await coro_func(*args, **kwargs)
            except Exception as e:
                is_retryable = any(isinstance(e, ex_type) for ex_type in self.retryable_exceptions)
                if not is_retryable or attempt == self.max_attempts:
                    last_error = e
                    break

                delay = self.exponential_backoff(attempt)
                await asyncio.sleep(delay)

        raise RetryExceededError(
            f"Max retry attempts ({self.max_attempts}) reached. Last error: {str(last_error)}"
        ) from last_error
