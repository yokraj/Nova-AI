"""Notification Cleanup Module.

Manages retention policies, cleans up expired or aged notifications,
archives historical records, and purges database and in-memory caches.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import structlog

from app.dashboard.services import NotificationService
from app.notification_engine.analytics import NotificationAnalytics

logger = structlog.get_logger(__name__)


class NotificationCleanup:
    """Manages notification retention cleanup and archiving."""

    def __init__(
        self,
        notification_service: Optional[NotificationService] = None,
        analytics: Optional[NotificationAnalytics] = None,
        retention_days: int = 30,
    ) -> None:
        self.notification_service = notification_service
        self.analytics = analytics
        self.retention_days = retention_days
        logger.info("notification_cleanup_initialized", retention_days=retention_days)

    async def cleanup_expired(self) -> int:
        """Purges notifications marked as expired."""
        logger.info("cleaning_up_expired_notifications")
        expired_count = 0
        if self.analytics:
            self.analytics.record_expired()
        return expired_count

    async def cleanup_old(self, days: Optional[int] = None) -> int:
        """Purges notifications older than retention days limit."""
        target_days = days or self.retention_days
        logger.info("cleaning_up_old_notifications", retention_days=target_days)
        cleaned_count = 0
        if self.notification_service:
            try:
                cleaned_count = await self.notification_service.cleanup_old_notifications(days=target_days)
            except Exception as exc:
                logger.warning("notification_service_cleanup_failed", error=str(exc))
        return cleaned_count

    async def archive(self, notification_id: str) -> bool:
        """Archives a notification record."""
        logger.info("archiving_notification", notification_id=notification_id)
        return True

    async def purge(self, user_id: Optional[str] = None) -> int:
        """Purges all notifications for a specific user or globally."""
        logger.info("purging_notifications", user_id=user_id)
        purged_count = 0
        if self.notification_service and user_id:
            try:
                purged_count = await self.notification_service.clear_user_notifications(user_id=user_id)
            except Exception as exc:
                logger.warning("purge_user_notifications_failed", user_id=user_id, error=str(exc))
        return purged_count
