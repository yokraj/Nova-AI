"""TimeoutManager managing timeout wrapper contexts.
"""

import asyncio
import time
from typing import Any, Coroutine, Optional

from app.agent_sdk.execution.exceptions import TimeoutError


class TimeoutManager:
    """Manages asyncio timeout wrapping loops."""

    def __init__(self) -> None:
        """Initializes TimeoutManager."""
        self._start_time: Optional[float] = None
        self._limit: Optional[float] = None

    async def execute_with_timeout(self, coro: Coroutine[Any, Any, Any], timeout_seconds: float) -> Any:
        """Executes a coroutine checking timeout constraints.

        Args:
            coro: Target coroutine task.
            timeout_seconds: Maximum allowed time in seconds.

        Returns:
            Target coroutine return value.

        Raises:
            TimeoutError: If execution exceeds timeout duration.
        """
        self._start_time = time.time()
        self._limit = timeout_seconds
        try:
            return await asyncio.wait_for(coro, timeout=timeout_seconds)
        except asyncio.TimeoutError as e:
            raise TimeoutError(f"Execution timed out after {timeout_seconds} seconds.") from e

    def remaining_time(self) -> float:
        """Calculates remaining time under the current timeout limit.

        Returns:
            Remaining float seconds, or 0.0 if expired or not set.
        """
        if self._start_time is None or self._limit is None:
            return 0.0
        elapsed = time.time() - self._start_time
        return max(0.0, self._limit - elapsed)
