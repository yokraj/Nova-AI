"""Event Bridge linking safety outcomes to system brokers.
"""

import structlog
from typing import Any
from app.ai.safety.models import AuditRecord

logger = structlog.get_logger("safety_event_bridge")

class SafetyEventBridge:
    """Dispatches core triggers for approval updates."""

    def __init__(self, system_bus: Any = None) -> None:
        self.system_bus = system_bus

    async def publish_audit(self, record: AuditRecord) -> None:
        """Publishes safety audit snapshots on transitions."""
        if self.system_bus:
            try:
                await self.system_bus.publish("safety_audit_logged", record.model_dump())
            except Exception as err:
                logger.error("Failed to forward audit signal via event bridge", error=str(err))
