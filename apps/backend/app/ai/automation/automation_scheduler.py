"""Automation Scheduler managing action timing, delays, and timeouts."""

import anyio
import structlog
from typing import Any, Callable

logger = structlog.get_logger("automation_scheduler")


class AutomationScheduler:
    """Schedules automation action execution with timeout enforcement."""

    async def execute_with_timeout(
        self,
        func: Callable[[], Any],
        timeout_seconds: float = 60.0,
    ) -> Any:
        """Run automation call inside AnyIO timeout guard."""
        with anyio.fail_after(timeout_seconds):
            if anyio.iscoroutinefunction(func):
                return await func()
            return func()
