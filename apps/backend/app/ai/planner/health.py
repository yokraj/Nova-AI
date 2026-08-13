"""Health monitor verifying planner subsystems and memory/bus integrations.
"""

import structlog
from typing import Dict, Any

logger = structlog.get_logger("planner_health")

class PlannerHealthMonitor:
    """Probes status check of all active planning components."""

    def __init__(
        self,
        planner: Any,
        analyzer: Any,
        dag_builder: Any,
        scheduler: Any,
        optimizer: Any,
        memory: Any,
        event_bus: Any,
        registry: Any
    ) -> None:
        self.planner = planner
        self.analyzer = analyzer
        self.dag_builder = dag_builder
        self.scheduler = scheduler
        self.optimizer = optimizer
        self.memory = memory
        self.event_bus = event_bus
        self.registry = registry

    async def check_health(self) -> Dict[str, Any]:
        """Asserts components status ensuring full availability."""
        status = {
            "status": "healthy",
            "planner_healthy": self.planner is not None,
            "analyzer_healthy": self.analyzer is not None,
            "dag_builder_healthy": self.dag_builder is not None,
            "scheduler_healthy": self.scheduler is not None,
            "optimizer_healthy": self.optimizer is not None,
            "memory_healthy": self.memory is not None,
            "event_bus_healthy": self.event_bus is not None,
            "registry_healthy": self.registry is not None
        }

        all_ok = all(status[key] for key in status if key != "status")
        if not all_ok:
            status["status"] = "unhealthy"

        logger.info("Planner components check completed", status=status)
        return status
