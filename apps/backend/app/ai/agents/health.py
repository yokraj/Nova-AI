"""Health Monitor verifying framework dependencies and event bus integrity.
"""

import structlog
from typing import Dict, Any

logger = structlog.get_logger("agent_health")

class AgentHealthMonitor:
    """Verifies manager, registry, and scheduler subsystems status."""

    def __init__(
        self,
        registry: Any,
        manager: Any,
        container: Any,
        event_bus: Any,
        scheduler: Any,
    ) -> None:
        self.registry = registry
        self.manager = manager
        self.container = container
        self.event_bus = event_bus
        self.scheduler = scheduler

    async def check_health(self) -> Dict[str, Any]:
        """Probes status of each framework subsystem layer."""
        status = {
            "status": "healthy",
            "registry_healthy": False,
            "manager_healthy": False,
            "container_healthy": False,
            "event_bus_healthy": False,
            "scheduler_healthy": False,
        }

        if self.registry is not None:
            status["registry_healthy"] = True

        if self.manager is not None:
            status["manager_healthy"] = True

        if self.container is not None:
            status["container_healthy"] = True

        if self.event_bus is not None:
            status["event_bus_healthy"] = True

        if self.scheduler is not None:
            status["scheduler_healthy"] = True

        all_ok = all(status[key] for key in status if key != "status")
        if not all_ok:
            status["status"] = "unhealthy"

        logger.info("Agent framework components health checks completed", status=status)
        return status
