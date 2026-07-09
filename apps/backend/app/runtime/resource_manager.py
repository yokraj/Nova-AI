"""Resource Manager service for the Nova AI Runtime Kernel.

Enforces resource allocation boundaries and monitors utilization percentages.
"""

from typing import Dict
import structlog

from app.runtime.exceptions import ResourceExhaustedException
from app.runtime.interfaces import IKernelService

logger = structlog.get_logger(__name__)


class ResourceManager(IKernelService):
    """Enforces thresholds and keeps records of allocations metrics."""

    def __init__(self, limits: Optional[Dict[str, float]] = None) -> None:
        """Initializes the ResourceManager.

        Args:
            limits: Dictionary mapping resource type keys to numerical limits.
        """
        self._limits: Dict[str, float] = limits or {
            "max_memory_mb": 4096.0,
            "max_cpu_percent": 90.0,
            "max_threads": 100.0,
        }
        self._allocations: Dict[str, float] = {k: 0.0 for k in self._limits}

    async def start(self) -> None:
        """Starts monitoring allocations."""
        logger.info("resource_manager_started")

    async def stop(self) -> None:
        """Releases all tracked allocations."""
        self._allocations = {k: 0.0 for k in self._limits}
        logger.info("resource_manager_stopped")

    @property
    def name(self) -> str:
        """Unique service name identifier."""
        return "resource_manager"

    def allocate(self, resource_type: str, amount: float) -> None:
        """Validates and registers resource consumption allocations.

        Args:
            resource_type: Target resource category (e.g. 'max_memory_mb').
            amount: Quantity to allocate.

        Raises:
            ResourceExhaustedException: If requested amount exceeds limit.
        """
        if resource_type not in self._limits:
            return

        limit = self._limits[resource_type]
        current = self._allocations.get(resource_type, 0.0)

        if current + amount > limit:
            logger.error(
                "resource_exhaustion_warning",
                resource=resource_type,
                current=current,
                requested=amount,
                limit=limit,
            )
            raise ResourceExhaustedException(
                f"Resource limits exceeded for '{resource_type}'. "
                f"Allocation requested: {amount}, current: {current}, max limit: {limit}"
            )

        self._allocations[resource_type] = current + amount
        logger.debug(
            "resource_allocated", resource=resource_type, allocated=amount
        )

    def release(self, resource_type: str, amount: float) -> None:
        """De-registers resource allocations consumption.

        Args:
            resource_type: Resource category identifier.
            amount: Quantity to release.
        """
        if resource_type not in self._allocations:
            return
        current = self._allocations[resource_type]
        self._allocations[resource_type] = max(0.0, current - amount)
        logger.debug(
            "resource_released", resource=resource_type, released=amount
        )

    def get_utilization(self) -> Dict[str, Dict[str, float]]:
        """Compiles allocation percentages.

        Returns:
            Dictionary mapping resource types to allocation ratios metadata.
        """
        utilization = {}
        for key, limit in self._limits.items():
            allocated = self._allocations.get(key, 0.0)
            percent = (allocated / limit) * 100.0 if limit > 0 else 0.0
            utilization[key] = {
                "allocated": allocated,
                "limit": limit,
                "percent": round(percent, 2),
            }
        return utilization


from typing import Optional
