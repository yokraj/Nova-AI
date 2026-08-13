"""Timeout Manager imposing execution duration limit constraints.
"""

import asyncio
from typing import Any, Callable, Coroutine
from app.ai.workflow.exceptions import ExecutionError

class TimeoutManager:
    """Tracks running execution limits and raises exceptions on expiration."""

    async def execute_with_timeout(self, awaitable: Coroutine[Any, Any, Any], timeout_seconds: int) -> Any:
        """Runs target awaitable, raising ExecutionError if timeout is exceeded."""
        try:
            return await asyncio.wait_for(awaitable, timeout=float(timeout_seconds))
        except asyncio.TimeoutError:
            raise ExecutionError(f"Step execution timed out after {timeout_seconds} seconds")
