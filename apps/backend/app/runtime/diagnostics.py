"""Diagnostics service consolidating system metrics for the Nova AI Runtime.

Aggregates service registries, health manager states, resource allocations,
and registered capability statistics.
"""

from typing import Any, Dict, List
import structlog

from app.runtime.health_manager import HealthManager
from app.runtime.interfaces import IKernelService
from app.runtime.resource_manager import ResourceManager
from app.runtime.service_registry import ServiceRegistry

logger = structlog.get_logger(__name__)


class RuntimeDiagnostics(IKernelService):
    """Aggregates and formats liveness checks reports for core subsystems."""

    def __init__(
        self,
        service_registry: ServiceRegistry,
        resource_manager: ResourceManager,
        health_manager: HealthManager,
    ) -> None:
        """Initializes the RuntimeDiagnostics.

        Args:
            service_registry: The core ServiceRegistry system.
            resource_manager: The core ResourceManager limits tracker.
            health_manager: The core HealthManager diagnostics system.
        """
        self.service_registry = service_registry
        self.resource_manager = resource_manager
        self.health_manager = health_manager

    async def start(self) -> None:
        """Starts diagnostic logging."""
        logger.info("runtime_diagnostics_started")

    async def stop(self) -> None:
        """Shuts down diagnostics."""
        logger.info("runtime_diagnostics_stopped")

    @property
    def name(self) -> str:
        """Unique service name identifier."""
        return "diagnostics"

    def get_diagnostics_report(
        self, active_capabilities: List[str]
    ) -> Dict[str, Any]:
        """Compiles health states and allocations indicators into a single schema.

        Args:
            active_capabilities: List of capability IDs currently active in manager.

        Returns:
            A dictionary containing structural platform diagnostics report.
        """
        return {
            "services": self.service_registry.list_services(),
            "resources": self.resource_manager.get_utilization(),
            "health": self.health_manager.get_service_statuses(),
            "loaded_capabilities": active_capabilities,
            "system_cpu_mock": 12.5,  # Mocked baseline execution load
            "system_memory_mock": 38.2,  # Mocked baseline memory usage percent
        }
