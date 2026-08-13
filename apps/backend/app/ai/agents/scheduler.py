"""Scheduler managing delayed and periodic agent tasks execution loops.
"""

import asyncio
import structlog
from typing import Any, Callable, Coroutine

logger = structlog.get_logger("agent_scheduler")

class AgentScheduler:
    """Tracks running tasks, allowing immediate, delayed, and periodic scheduling."""

    def __init__(self) -> None:
        self._running_tasks: set[asyncio.Task] = set()

    def schedule_immediate(self, coro: Coroutine[Any, Any, None]) -> asyncio.Task:
        """Schedules coroutine for immediate execution as a background task."""
        task = asyncio.create_task(coro)
        self._running_tasks.add(task)
        task.add_done_callback(self._running_tasks.discard)
        return task

    def schedule_delayed(self, delay_seconds: float, coro: Coroutine[Any, Any, None]) -> asyncio.Task:
        """Schedules execution to start after a specific delay."""
        async def _run_delayed() -> None:
            await asyncio.sleep(delay_seconds)
            await coro
        return self.schedule_immediate(_run_delayed())

    def schedule_periodic(self, interval_seconds: float, func: Callable[[], Coroutine[Any, Any, None]]) -> asyncio.Task:
        """Schedules continuous execution at defined time intervals."""
        async def _run_periodic() -> None:
            while True:
                try:
                    await func()
                except asyncio.CancelledError:
                    break
                except Exception as err:
                    logger.error("Error executing scheduled periodic task", error=str(err))
                await asyncio.sleep(interval_seconds)
        return self.schedule_immediate(_run_periodic())

    def shutdown(self) -> None:
        """Cancels all active background tasks."""
        for task in list(self._running_tasks):
            if not task.done():
                task.cancel()
        logger.info("Scheduler successfully shut down, cancelled background tasks", active_tasks=len(self._running_tasks))
