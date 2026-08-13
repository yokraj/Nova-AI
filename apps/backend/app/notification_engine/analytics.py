"""Notification Analytics Module.

Tracks notification metrics across lifecycle stages (creation, delivery, read state,
expiration, deletions, duplicates, delivery failures, latencies, and priority distribution).
"""

from typing import Any, Dict
import structlog

logger = structlog.get_logger(__name__)


class NotificationAnalytics:
    """Notification platform performance and telemetry analytics tracker."""

    def __init__(self) -> None:
        self.notifications_created: int = 0
        self.notifications_delivered: int = 0
        self.notifications_read: int = 0
        self.notifications_expired: int = 0
        self.notifications_deleted: int = 0
        self.duplicate_notifications: int = 0
        self.delivery_failures: int = 0
        self.total_delivery_time_ms: float = 0.0

        self.priority_distribution: Dict[str, int] = {
            "LOW": 0,
            "NORMAL": 0,
            "HIGH": 0,
            "URGENT": 0,
        }

        logger.info("notification_analytics_initialized")

    def record_created(self, priority: str = "NORMAL") -> None:
        """Records notification creation."""
        self.notifications_created += 1
        prio = str(priority).upper()
        if prio in self.priority_distribution:
            self.priority_distribution[prio] += 1

    def record_delivered(self, duration_ms: float = 0.0) -> None:
        """Records successful WebSocket delivery."""
        self.notifications_delivered += 1
        self.total_delivery_time_ms += duration_ms

    def record_read(self) -> None:
        """Records notification mark as read event."""
        self.notifications_read += 1

    def record_expired(self) -> None:
        """Records notification expiration."""
        self.notifications_expired += 1

    def record_deleted(self) -> None:
        """Records notification deletion."""
        self.notifications_deleted += 1

    def record_duplicate(self) -> None:
        """Records duplicate notification rejection."""
        self.duplicate_notifications += 1

    def record_failure(self) -> None:
        """Records delivery failure."""
        self.delivery_failures += 1

    def get_summary(self) -> Dict[str, Any]:
        """Returns analytics telemetry summary dictionary."""
        avg_delivery_time = (
            (self.total_delivery_time_ms / self.notifications_delivered)
            if self.notifications_delivered > 0
            else 0.0
        )

        return {
            "notifications_created": self.notifications_created,
            "notifications_delivered": self.notifications_delivered,
            "notifications_read": self.notifications_read,
            "notifications_expired": self.notifications_expired,
            "notifications_deleted": self.notifications_deleted,
            "duplicate_notifications": self.duplicate_notifications,
            "delivery_failures": self.delivery_failures,
            "average_delivery_time_ms": round(avg_delivery_time, 2),
            "priority_distribution": self.priority_distribution,
        }

    def reset(self) -> None:
        """Resets all analytics counters."""
        self.notifications_created = 0
        self.notifications_delivered = 0
        self.notifications_read = 0
        self.notifications_expired = 0
        self.notifications_deleted = 0
        self.duplicate_notifications = 0
        self.delivery_failures = 0
        self.total_delivery_time_ms = 0.0
        self.priority_distribution = {"LOW": 0, "NORMAL": 0, "HIGH": 0, "URGENT": 0}
