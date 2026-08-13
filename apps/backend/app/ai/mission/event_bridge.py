"""Event Bridge dispatching mission transition signals.
"""

import structlog
from typing import Any
from app.ai.mission.models import Mission

logger = structlog.get_logger("mission_event_bridge")

class MissionEventBridge:
    """Dispatches core event triggers for lifecycle transitions."""

    def __init__(self, system_bus: Any = None) -> None:
        self.system_bus = system_bus

    async def publish_mission_transition(self, mission: Mission) -> None:
        """Publishes mission snapshots on lifecycle transitions."""
        if self.system_bus:
            try:
                await self.system_bus.publish("mission_state_changed", {
                    "mission_id": mission.mission_id,
                    "state": mission.state.value,
                    "progress": mission.progress
                })
            except Exception as err:
                logger.error("Failed to forward mission signal via event bridge", error=str(err))
