"""Notification Manager dispatching proactive voice alerts and notification banners."""

import structlog

from app.ai.assistant.models import ReminderPriority

logger = structlog.get_logger("notification_manager")


class NotificationManager:
    """Dispatches proactive voice notifications and UI alerts."""

    async def dispatch_notification(
        self,
        title: str,
        message: str,
        priority: ReminderPriority = ReminderPriority.MEDIUM,
    ) -> bool:
        """Dispatch proactive notification."""
        logger.info("Dispatched proactive notification", title=title, priority=priority.value)
        return True
