"""Resource Monitor Service Module.

Provides database repository queries and persistence for CPU, Memory, Disk, Network,
GPU, and Process hardware metrics without live OS sampling.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.dashboard.exceptions import MetricNotFoundError
from app.dashboard.repositories import MetricsRepository
from app.dashboard.schemas import ResourceMetricCreate
from app.database.models.dashboard import GPUMetric, ProcessMetric, ResourceMetric
from app.database.models.enums import ResourceType

logger = structlog.get_logger(__name__)


class ResourceMonitorService:
    """Service layer for persisting and retrieving resource-specific metrics."""

    def __init__(self, metrics_repository: MetricsRepository) -> None:
        self.metrics_repository = metrics_repository
        logger.info("resource_monitor_service_initialized")

    async def store_resource_metrics(self, data: ResourceMetricCreate) -> ResourceMetric:
        """Stores a new resource metric sample into repository."""
        metric = ResourceMetric(
            timestamp=data.timestamp,
            resource_type=data.resource_type.value if hasattr(data.resource_type, "value") else str(data.resource_type),
            resource_name=data.resource_name,
            current_value=data.current_value,
            maximum_value=data.maximum_value,
            percentage=data.percentage,
            unit=data.unit,
            status=data.status,
        )
        stored = await self.metrics_repository.create(metric)
        logger.info(
            "resource_metrics_stored",
            metric_id=str(stored.id),
            resource_type=stored.resource_type,
            resource_name=data.resource_name,
        )
        return stored

    async def get_resource_history(
        self, resource_type: Optional[str] = None, limit: int = 100
    ) -> List[ResourceMetric]:
        """Retrieves historical resource metrics optionally filtered by resource type."""
        all_metrics = await self.metrics_repository.resource.list(skip=0, limit=limit)
        if resource_type:
            target_type = resource_type.lower()
            return [m for m in all_metrics if m.resource_type.lower() == target_type]
        return all_metrics

    async def get_cpu_metrics(self) -> List[ResourceMetric]:
        """Retrieves latest CPU metrics from stored repository records."""
        return await self.get_resource_history(resource_type=ResourceType.CPU.value, limit=50)

    async def get_memory_metrics(self) -> List[ResourceMetric]:
        """Retrieves latest Memory metrics from stored repository records."""
        return await self.get_resource_history(resource_type=ResourceType.MEMORY.value, limit=50)

    async def get_disk_metrics(self) -> List[ResourceMetric]:
        """Retrieves latest Disk storage metrics from stored repository records."""
        return await self.get_resource_history(resource_type=ResourceType.DISK.value, limit=50)

    async def get_network_metrics(self) -> List[ResourceMetric]:
        """Retrieves latest Network interface metrics from stored repository records."""
        return await self.get_resource_history(resource_type=ResourceType.NETWORK.value, limit=50)

    async def get_gpu_metrics(self) -> List[GPUMetric]:
        """Retrieves stored GPU metrics from repository."""
        return await self.metrics_repository.gpu.list(skip=0, limit=50)

    async def get_process_metrics(self) -> List[ProcessMetric]:
        """Retrieves stored Process table metrics from repository."""
        return await self.metrics_repository.process.list(skip=0, limit=50)
