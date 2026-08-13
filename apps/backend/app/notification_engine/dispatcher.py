"""Notification Dispatcher Module.

Runs background processing loops, popping queued notifications from NotificationQueue,
persisting through NotificationService, and delivering real-time alerts.
"""

import asyncio
from datetime import datetime, timezone
import time
from typing import Any, Dict, Optional
import structlog

from app.dashboard.schemas import DashboardNotificationCreate
from app.dashboard.services import NotificationService
from app.database.models.enums import NotificationPriority
from app.notification_engine.analytics import NotificationAnalytics
from app.notification_engine.delivery import NotificationDeliveryManager
from app.notification_engine.queue import NotificationQueue

logger = structlog.get_logger(__name__)


class NotificationDispatcher:
    """Async background worker dispatching notifications from priority queue to WebSocket channels."""

    def __init__(
        self,
        queue: NotificationQueue,
        delivery_manager: NotificationDeliveryManager,
        notification_service: Optional[NotificationService] = None,
        analytics: Optional[NotificationAnalytics] = None,
    ) -> None:
        self.queue = queue
        self.delivery_manager = delivery_manager
        self.notification_service = notification_service
        self.analytics = analytics
        self._running = False
        self._task: Optional[asyncio.Task] = None

        logger.info("notification_dispatcher_initialized")

    async def process_one(self) -> Optional[Dict[str, Any]]:
        """Pops highest priority notification from queue and dispatches it."""
        item = await self.queue.dequeue()
        if not item:
            return None

        start_time = time.time()

        # 1. Persist in DB via NotificationService if present
        if self.notification_service:
            try:
                prio_str = str(item.get("priority", "NORMAL")).upper()
                try:
                    prio_enum = NotificationPriority[prio_str]
                except KeyError:
                    prio_enum = NotificationPriority.NORMAL

                dto = DashboardNotificationCreate(
                    title=item.get("title", "Alert"),
                    message=item.get("message", ""),
                    type=item.get("category", "system"),
                    priority=prio_enum,
                )
                db_record = await self.notification_service.create_notification(dto)
                item["id"] = str(db_record.id)
            except Exception as exc:
                logger.warning("notification_db_persist_failed", error=str(exc))

        # 2. Deliver over WebSocket Gateway
        try:
            await self.delivery_manager.deliver_realtime(item)
            duration_ms = (time.time() - start_time) * 1000.0
            if self.analytics:
                self.analytics.record_delivered(duration_ms)
        except Exception as exc:
            logger.error("notification_dispatch_delivery_failed", error=str(exc))
            if self.analytics:
                self.analytics.record_failure()

        return item

    async def _dispatch_loop(self) -> None:
        """Continuous background dispatching worker loop."""
        while self._running:
            try:
                processed = await self.process_one()
                if not processed:
                    await asyncio.sleep(0.05)
            except Exception as exc:
                logger.error("notification_dispatch_loop_error", error=str(exc))
                await asyncio.sleep(0.1)

    def start(self) -> None:
        """Starts background dispatcher worker task."""
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._dispatch_loop())
            logger.info("notification_dispatcher_started")

    def stop(self) -> None:
        """Stops background dispatcher worker task."""
        if self._running:
            self._running = False
            if self._task and not self._task.done():
                self._task.cancel()
            logger.info("notification_dispatcher_stopped")
