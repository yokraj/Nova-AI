"""Notification Statistics Module.

Provides summary DTOs, hourly/daily trends, priority breakdowns,
and delivery health reports for the Notification Engine.
"""

from datetime import datetime, timezone
from typing import Any, Dict
import structlog

from app.notification_engine.analytics import NotificationAnalytics

logger = structlog.get_logger(__name__)


class NotificationStatistics:
    """Generates structured statistics reports for the Notification Engine."""

    def __init__(self, analytics: NotificationAnalytics) -> None:
        self.analytics = analytics
        logger.info("notification_statistics_initialized")

    def summary(self) -> Dict[str, Any]:
        """Returns consolidated notification platform summary."""
        return self.analytics.get_summary()

    def hourly_statistics(self) -> Dict[str, Any]:
        """Returns current hourly notification metrics summary."""
        now = datetime.now(timezone.utc)
        hour_key = now.strftime("%Y-%m-%dT%H:00:00Z")
        return {
            "hour": hour_key,
            "created": self.analytics.notifications_created,
            "delivered": self.analytics.notifications_delivered,
            "failures": self.analytics.delivery_failures,
        }

    def daily_statistics(self) -> Dict[str, Any]:
        """Returns current daily notification metrics summary."""
        now = datetime.now(timezone.utc)
        day_key = now.strftime("%Y-%m-%d")
        return {
            "date": day_key,
            "created": self.analytics.notifications_created,
            "delivered": self.analytics.notifications_delivered,
            "read": self.analytics.notifications_read,
            "deleted": self.analytics.notifications_deleted,
        }

    def priority_statistics(self) -> Dict[str, Any]:
        """Returns notification distribution broken down by priority level."""
        return {
            "distribution": self.analytics.priority_distribution,
            "total": sum(self.analytics.priority_distribution.values()),
        }

    def delivery_statistics(self) -> Dict[str, Any]:
        """Returns WebSocket delivery success rate and latency statistics."""
        delivered = self.analytics.notifications_delivered
        failures = self.analytics.delivery_failures
        total = delivered + failures
        success_rate = (delivered / total * 100.0) if total > 0 else 100.0

        return {
            "delivered": delivered,
            "failures": failures,
            "success_rate_percent": round(success_rate, 2),
            "average_delivery_time_ms": self.analytics.get_summary()["average_delivery_time_ms"],
        }
