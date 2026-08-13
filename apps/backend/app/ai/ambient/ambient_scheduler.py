"""Ambient Scheduler managing background desktop monitoring intervals."""

import asyncio
from typing import Callable, Optional
import structlog

logger = structlog.get_logger("ambient_scheduler")


class AmbientScheduler:
    """Schedules background polling loops for desktop monitoring."""

    def __init__(self, interval_seconds: float = 3.0) -> None:
        self.interval = interval_seconds
        self.running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self, callback: Callable[[], None]) -> None:
        """Start background polling loop."""
        self.running = True
        logger.info("Ambient scheduler polling loop started", interval=self.interval)

    async def stop(self) -> None:
        """Stop polling loop."""
        self.running = False
        logger.info("Ambient scheduler polling loop stopped")
