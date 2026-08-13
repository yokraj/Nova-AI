"""Notification Service Module.

Provides notification management, alert creation, mark read/unread operations,
deletion, unread counters, and expiration cleanup via repositories.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
import structlog

from app.dashboard.exceptions import NotificationNotFoundError
from app.dashboard.repositories import NotificationRepository
from app.dashboard.schemas import DashboardNotificationCreate, DashboardNotificationUpdate
from app.database.models.dashboard import DashboardNotification

logger = structlog.get_logger(__name__)


class NotificationService:
    """Service layer for dashboard notifications and user alert management."""

    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository
        logger.info("notification_service_initialized")

    async def create_notification(
        self, data: DashboardNotificationCreate
    ) -> DashboardNotification:
        """Creates a new dashboard notification record."""
        notification = DashboardNotification(
            snapshot_id=data.snapshot_id,
            type=data.type,
            priority=data.priority.value if hasattr(data.priority, "value") else str(data.priority),
            title=data.title,
            message=data.message,
            read=data.read,
            read_at=data.read_at,
            expires_at=data.expires_at,
        )
        created = await self.repository.create(notification)
        logger.info("notification_created", notification_id=str(created.id), title=data.title)
        return created

    async def mark_as_read(self, notification_id: uuid.UUID) -> DashboardNotification:
        """Marks a notification as read with timestamp."""
        now = datetime.now(timezone.utc)
        updated = await self.repository.update(
            notification_id, {"read": True, "read_at": now}
        )
        if not updated:
            raise NotificationNotFoundError(str(notification_id))
        logger.info("notification_marked_read", notification_id=str(notification_id))
        return updated

    async def mark_all_read(self) -> int:
        """Marks all unread notifications as read."""
        unread_notifications = await self.get_notifications(limit=1000, unread_only=True)
        now = datetime.now(timezone.utc)
        count = 0
        for n in unread_notifications:
            await self.repository.update(n.id, {"read": True, "read_at": now})
            count += 1
        logger.info("all_notifications_marked_read", count=count)
        return count

    async def delete_notification(self, notification_id: uuid.UUID) -> DashboardNotification:
        """Deletes a notification record by ID."""
        deleted = await self.repository.delete(notification_id)
        if not deleted:
            raise NotificationNotFoundError(str(notification_id))
        logger.info("notification_deleted", notification_id=str(notification_id))
        return deleted

    async def get_notifications(
        self, limit: int = 100, unread_only: bool = False
    ) -> List[DashboardNotification]:
        """Retrieves dashboard notifications list."""
        all_notifs = await self.repository.list(skip=0, limit=limit)
        if unread_only:
            return [n for n in all_notifs if not n.read]
        return all_notifs

    async def get_unread_count(self) -> int:
        """Returns the total number of unread notifications."""
        unread = await self.get_notifications(limit=1000, unread_only=True)
        return len(unread)

    async def cleanup_expired(self) -> int:
        """Deletes all notifications whose expiration timestamp has passed."""
        all_notifs = await self.repository.list(skip=0, limit=1000)
        now = datetime.now(timezone.utc)
        count = 0
        for n in all_notifs:
            if n.expires_at and n.expires_at <= now:
                await self.repository.delete(n.id)
                count += 1
        logger.info("expired_notifications_cleaned_up", count=count)
        return count
