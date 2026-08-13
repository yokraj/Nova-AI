"""Notification Delivery Manager Module.

Dispatches real-time notifications over WebSocket Gateway using existing
DashboardBroadcaster to target streaming channels ('notifications', 'dashboard').
"""

from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
import structlog

from app.notification_engine.exceptions import NotificationDeliveryError
from app.websocket.broadcaster import DashboardBroadcaster

logger = structlog.get_logger(__name__)


class NotificationDeliveryManager:
    """Delivers real-time notification payloads over WebSocket channels via DashboardBroadcaster."""

    def __init__(self, broadcaster: DashboardBroadcaster, retry_limit: int = 3) -> None:
        self.broadcaster = broadcaster
        self.retry_limit = retry_limit
        logger.info("notification_delivery_manager_initialized", retry_limit=retry_limit)

    async def deliver_realtime(self, notification: Dict[str, Any]) -> bool:
        """Broadcasts single notification over WebSocket 'notifications' and 'dashboard' channels."""
        try:
            # 1. Broadcast on notifications channel
            await self.broadcaster.broadcast_notifications(notification)

            # 2. If URGENT or HIGH priority, also broadcast on consolidated dashboard channel
            prio = str(notification.get("priority", "")).upper()
            if prio in ["HIGH", "URGENT"]:
                await self.broadcaster.broadcast_dashboard({
                    "type": "urgent_notification",
                    "notification": notification,
                })

            logger.info("notification_delivered_realtime", notification_id=notification.get("id"), title=notification.get("title"))
            return True
        except Exception as exc:
            logger.warning("notification_realtime_delivery_failed", notification_id=notification.get("id"), error=str(exc))
            raise NotificationDeliveryError(str(notification.get("id", "unknown")), str(exc)) from exc

    async def deliver(self, notification: Dict[str, Any]) -> bool:
        """Alias for deliver_realtime."""
        return await self.deliver_realtime(notification)

    async def deliver_batch(self, notifications: List[Dict[str, Any]]) -> int:
        """Delivers a batch list of notifications."""
        delivered_count = 0
        for notif in notifications:
            try:
                if await self.deliver_realtime(notif):
                    delivered_count += 1
            except Exception as exc:
                logger.warning("batch_delivery_item_failed", error=str(exc))
        return delivered_count

    async def retry_failed(self, notification: Dict[str, Any]) -> bool:
        """Retries delivery of a failed notification up to retry_limit attempts."""
        attempts = notification.get("retry_count", 0) + 1
        notification["retry_count"] = attempts

        if attempts > self.retry_limit:
            logger.error("notification_retry_limit_exceeded", notification_id=notification.get("id"), attempts=attempts)
            return False

        logger.info("retrying_notification_delivery", notification_id=notification.get("id"), attempt=attempts)
        try:
            return await self.deliver_realtime(notification)
        except Exception:
            return False

    def expire(self, notification_id: str) -> None:
        """Marks a notification ID as expired."""
        logger.info("notification_marked_expired", notification_id=notification_id)
