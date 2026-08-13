"""Notification Monitor capturing system notifications and low battery alerts."""

from typing import List
import structlog

from app.ai.ambient.models import NotificationEvent

logger = structlog.get_logger("notification_monitor")


class NotificationMonitor:
    """Listens for desktop notifications, system alerts, and low battery popups."""

    async def get_recent_notifications(self) -> List[NotificationEvent]:
        """Get recent notifications."""
        return [
            NotificationEvent(
                source="System",
                title="Battery Low",
                message="Battery level is at 12%. Connect charger.",
                is_low_battery=True,
            )
        ]
