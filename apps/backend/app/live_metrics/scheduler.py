"""Metrics Scheduler Module.

Orchestrates asynchronous continuous metric collection and snapshot cleanup loops
using native asyncio background tasks (no external cron or APScheduler dependencies).
"""

import asyncio
from typing import Awaitable, Callable, Optional
import structlog

from app.live_metrics.exceptions import SchedulerError

logger = structlog.get_logger(__name__)


class MetricsScheduler:
    """Async background task scheduler for periodic telemetry collection and cleanup."""

    def __init__(
        self,
        collection_callback: Callable[[], Awaitable[None]],
        cleanup_callback: Optional[Callable[[], Awaitable[None]]] = None,
        collection_interval: float = 1.0,
        cleanup_interval: float = 60.0,
    ) -> None:
        self.collection_callback = collection_callback
        self.cleanup_callback = cleanup_callback
        self.collection_interval = collection_interval
        self.cleanup_interval = cleanup_interval

        self._running = False
        self._paused = False
        self._collection_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None

        logger.info(
            "metrics_scheduler_initialized",
            collection_interval=collection_interval,
            cleanup_interval=cleanup_interval,
        )

    @property
    def is_running(self) -> bool:
        """Returns True if background loops are active."""
        return self._running

    @property
    def is_paused(self) -> bool:
        """Returns True if scheduler is paused."""
        return self._paused

    async def run_collection_loop(self) -> None:
        """Periodic background collection loop."""
        while self._running:
            if not self._paused:
                try:
                    await self.collection_callback()
                except Exception as exc:
                    logger.error("scheduler_collection_loop_error", error=str(exc))
            await asyncio.sleep(self.collection_interval)

    async def run_cleanup_loop(self) -> None:
        """Periodic background cleanup loop."""
        while self._running:
            if not self._paused and self.cleanup_callback:
                try:
                    await self.cleanup_callback()
                except Exception as exc:
                    logger.error("scheduler_cleanup_loop_error", error=str(exc))
            await asyncio.sleep(self.cleanup_interval)

    def start(self) -> None:
        """Starts asynchronous background collection and cleanup loops."""
        if not self._running:
            self._running = True
            self._paused = False
            self._collection_task = asyncio.create_task(self.run_collection_loop())
            if self.cleanup_callback:
                self._cleanup_task = asyncio.create_task(self.run_cleanup_loop())
            logger.info("metrics_scheduler_started")

    def stop(self) -> None:
        """Stops background loops and cancels active tasks."""
        if self._running:
            self._running = False
            self._paused = False

            if self._collection_task and not self._collection_task.done():
                self._collection_task.cancel()
            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()

            logger.info("metrics_scheduler_stopped")

    def pause(self) -> None:
        """Pauses metric collection execution without destroying background tasks."""
        if self._running and not self._paused:
            self._paused = True
            logger.info("metrics_scheduler_paused")

    def resume(self) -> None:
        """Resumes metric collection execution."""
        if self._running and self._paused:
            self._paused = False
            logger.info("metrics_scheduler_resumed")
