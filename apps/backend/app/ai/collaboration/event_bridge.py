"""Event Bridge bridging local collaboration events to the system event bus.
"""

import structlog
from typing import Any
from app.ai.collaboration.models import StructuredMessage

logger = structlog.get_logger("event_bridge")

class EventBridge:
    """Manages stream bridges connecting internal message lines with system gateways."""

    def __init__(self, comm_bus: Any, event_bus: Any) -> None:
        self.comm_bus = comm_bus
        self.event_bus = event_bus

    async def forward_to_system(self, message: StructuredMessage) -> None:
        """Forwards inter-agent messages directly to the system event broker."""
        if self.event_bus:
            try:
                await self.event_bus.publish(f"collab_{message.message_type.value.lower()}", message)
            except Exception as err:
                logger.error("Failed to forward message via event bridge", error=str(err))
