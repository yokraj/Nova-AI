"""Notification Manager triggering alerts on lifecycle phase shifts.
"""

import structlog
from typing import Any

logger = structlog.get_logger("mission_notifications")

class NotificationManager:
    """Fires state updates alerts and hooks."""

    def __init__(self, system_bus: Any = None) -> None:
        self.system_bus = system_bus

    async def notify_event(self, event_name: str, payload: Any) -> None:
        """Publishes notification alert to core event systems."""
        logger.info("Mission Notification", event_type=event_name, payload=payload)
        if self.system_bus:
            try:
                await self.system_bus.publish("mission_notification", {
                    "event": event_name,
                    "payload": payload
                })
            except Exception as err:
                logger.error("Failed to forward notification message", error=str(err))
