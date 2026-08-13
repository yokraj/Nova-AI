"""Notification Engine Master Orchestrator Module.

Unites NotificationConfig, RuleEngine, PriorityManager, Deduplicator, Queue,
DeliveryManager, Dispatcher, Analytics, Statistics, and Cleanup into an event-driven
enterprise notification platform.
"""

import asyncio
from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional
import structlog

from app.dashboard.services import NotificationService
from app.notification_engine.analytics import NotificationAnalytics
from app.notification_engine.cleanup import NotificationCleanup
from app.notification_engine.config import NotificationConfig
from app.notification_engine.deduplication import NotificationDeduplicator
from app.notification_engine.delivery import NotificationDeliveryManager
from app.notification_engine.dispatcher import NotificationDispatcher
from app.notification_engine.exceptions import (
    DuplicateNotificationError,
    NotificationEngineError,
)
from app.notification_engine.priority import (
    NotificationPriorityLevel,
    NotificationPriorityManager,
)
from app.notification_engine.queue import NotificationQueue
from app.notification_engine.rules import NotificationRuleEngine
from app.notification_engine.statistics import NotificationStatistics
from app.websocket.broadcaster import DashboardBroadcaster
from app.websocket.manager import ConnectionManager

logger = structlog.get_logger(__name__)


class NotificationEngine:
    """Enterprise Master Orchestrator for Event-Driven Notifications."""

    def __init__(
        self,
        config: Optional[NotificationConfig] = None,
        notification_service: Optional[NotificationService] = None,
        connection_manager: Optional[ConnectionManager] = None,
        broadcaster: Optional[DashboardBroadcaster] = None,
    ) -> None:
        self.config = config or NotificationConfig()
        self.notification_service = notification_service
        self.connection_manager = connection_manager or ConnectionManager()
        self.broadcaster = broadcaster or DashboardBroadcaster(manager=self.connection_manager)

        self.rule_engine = NotificationRuleEngine()
        self.priority_manager = NotificationPriorityManager(thresholds=self.config.priority_thresholds)
        self.deduplicator = NotificationDeduplicator(window_seconds=float(self.config.duplicate_window))
        self.queue = NotificationQueue(capacity=self.config.max_notifications)
        self.delivery_manager = NotificationDeliveryManager(
            broadcaster=self.broadcaster, retry_limit=self.config.delivery_retry_limit
        )
        self.analytics = NotificationAnalytics()
        self.statistics = NotificationStatistics(analytics=self.analytics)
        self.cleanup = NotificationCleanup(
            notification_service=self.notification_service,
            analytics=self.analytics,
            retention_days=self.config.notification_retention_days,
        )
        self.dispatcher = NotificationDispatcher(
            queue=self.queue,
            delivery_manager=self.delivery_manager,
            notification_service=self.notification_service,
            analytics=self.analytics,
        )

        self._running = False
        self._paused = False

        logger.info("notification_engine_initialized", config=self.config.model_dump())

    def start(self) -> None:
        """Starts the Notification Engine and background dispatcher worker."""
        if not self._running:
            self._running = True
            self._paused = False
            self.dispatcher.start()
            logger.info("notification_engine_started")

    def stop(self) -> None:
        """Stops the Notification Engine and background workers."""
        if self._running:
            self._running = False
            self._paused = False
            self.dispatcher.stop()
            logger.info("notification_engine_stopped")

    def pause(self) -> None:
        """Pauses background notification dispatching."""
        if self._running and not self._paused:
            self._paused = True
            self.dispatcher.stop()
            logger.info("notification_engine_paused")

    def resume(self) -> None:
        """Resumes background notification dispatching."""
        if self._running and self._paused:
            self._paused = False
            self.dispatcher.start()
            logger.info("notification_engine_resumed")

    async def create_notification(
        self,
        title: str,
        message: str,
        category: str = "system",
        priority: str = "NORMAL",
        component: Optional[str] = None,
        action_url: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates, deduplicates, enqueues, and dispatches a notification."""
        prio_enum = NotificationPriorityLevel[priority.upper()] if isinstance(priority, str) and priority.upper() in NotificationPriorityLevel.__members__ else NotificationPriorityLevel.NORMAL

        payload = {
            "id": str(uuid.uuid4()),
            "title": title,
            "message": message,
            "category": category,
            "priority": prio_enum.value,
            "component": component,
            "action_url": action_url,
            "user_id": user_id,
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # 1. Deduplication Check
        if self.deduplicator.is_duplicate(payload):
            self.analytics.record_duplicate()
            logger.info("notification_skipped_duplicate", title=title)
            raise DuplicateNotificationError(self.deduplicator._generate_fingerprint(payload))

        self.deduplicator.register(payload)
        self.analytics.record_created(priority=prio_enum.value)

        # 2. Enqueue in Priority Queue
        await self.queue.enqueue(payload)

        # 3. Direct processing if dispatcher isn't running
        if not self._running or self._paused:
            await self.dispatcher.process_one()

        return payload

    async def process_notification(self, event_name: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluates domain event against RuleEngine and creates notifications for matching rules."""
        generated = self.rule_engine.evaluate(event_name, payload)
        results = []

        for notif_data in generated:
            try:
                created = await self.create_notification(
                    title=notif_data["title"],
                    message=notif_data["message"],
                    category=notif_data.get("category", "system"),
                    priority=notif_data.get("priority", NotificationPriorityLevel.NORMAL).value if isinstance(notif_data.get("priority"), NotificationPriorityLevel) else str(notif_data.get("priority", "NORMAL")),
                    component=notif_data.get("component"),
                    user_id=payload.get("user_id"),
                )
                results.append(created)
            except DuplicateNotificationError:
                pass
            except Exception as exc:
                logger.warning("notification_process_rule_item_failed", event_name=event_name, error=str(exc))

        return results

    async def dispatch_notification(self, notification: Dict[str, Any]) -> bool:
        """Enqueues or delivers notification directly."""
        return await self.delivery_manager.deliver_realtime(notification)

    async def mark_as_read(self, notification_id: str) -> bool:
        """Marks a notification as read in database and updates analytics."""
        self.analytics.record_read()
        if self.notification_service:
            try:
                await self.notification_service.mark_as_read(notification_id)
            except Exception as exc:
                logger.warning("mark_as_read_db_failed", notification_id=notification_id, error=str(exc))
        return True

    async def mark_all_read(self, user_id: str) -> int:
        """Marks all notifications as read for user_id."""
        read_count = 0
        if self.notification_service:
            try:
                read_count = await self.notification_service.mark_all_as_read(user_id=user_id)
            except Exception as exc:
                logger.warning("mark_all_read_db_failed", user_id=user_id, error=str(exc))
        return read_count

    async def delete_notification(self, notification_id: str) -> bool:
        """Deletes a notification record."""
        self.analytics.record_deleted()
        if self.notification_service:
            try:
                await self.notification_service.delete_notification(notification_id)
            except Exception as exc:
                logger.warning("delete_notification_db_failed", notification_id=notification_id, error=str(exc))
        return True

    async def cleanup_notifications(self) -> int:
        """Executes retention cleanup."""
        return await self.cleanup.cleanup_old()

    async def get_notification_history(self, user_id: Optional[str] = None, limit: int = 50) -> List[Any]:
        """Returns notification history list from NotificationService."""
        if self.notification_service:
            try:
                return await self.notification_service.list_notifications(user_id=user_id, limit=limit)
            except Exception as exc:
                logger.warning("list_notifications_failed", error=str(exc))
        return []

    async def get_unread_count(self, user_id: Optional[str] = None) -> int:
        """Returns count of unread notifications."""
        if self.notification_service:
            try:
                return await self.notification_service.get_unread_count(user_id=user_id)
            except Exception as exc:
                logger.warning("get_unread_count_failed", error=str(exc))
        return 0
