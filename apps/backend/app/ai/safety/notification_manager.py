"""Notification Manager sending safety alerts to the event bus.
"""

import structlog
from typing import Any

logger = structlog.get_logger("safety_notifications")

class NotificationManager:
    """Fires safety triggers and alerts."""

    def __init__(self, system_bus: Any = None) -> None:
        self.system_bus = system_bus

    async def notify_approval_required(self, approval_id: str, prompt: str) -> None:
        """Alerts the core system that user confirmation is required."""
        logger.info("Human approval required", approval_id=approval_id, prompt=prompt)
        if self.system_bus:
            try:
                await self.system_bus.publish("approval_required", {
                    "approval_id": approval_id,
                    "prompt": prompt
                })
            except Exception as err:
                logger.error("Failed to publish approval alert", error=str(err))
