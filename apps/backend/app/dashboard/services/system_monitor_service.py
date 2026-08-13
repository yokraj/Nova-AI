"""System Monitor Service Module.

Provides repository-backed persistence and history query interfaces for system node metrics,
hostname, operating system parameters, and uptime tracking.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.dashboard.exceptions import MetricNotFoundError
from app.dashboard.repositories import MetricsRepository
from app.dashboard.schemas import SystemMetricCreate
from app.database.models.dashboard import SystemMetric

logger = structlog.get_logger(__name__)


class SystemMonitorService:
    """Service layer for persisting and retrieving system metrics from database storage."""

    def __init__(self, metrics_repository: MetricsRepository) -> None:
        self.metrics_repository = metrics_repository
        logger.info("system_monitor_service_initialized")

    async def store_system_metrics(self, data: SystemMetricCreate) -> SystemMetric:
        """Stores a new system metric sample in repository."""
        metric = SystemMetric(
            timestamp=data.timestamp,
            hostname=data.hostname,
            os_name=data.os_name,
            cpu_usage=data.cpu_usage,
            cpu_temperature=data.cpu_temperature,
            memory_total=data.memory_total,
            memory_used=data.memory_used,
            memory_available=data.memory_available,
            swap_used=data.swap_used,
            disk_total=data.disk_total,
            disk_used=data.disk_used,
            network_upload=data.network_upload,
            network_download=data.network_download,
            uptime=data.uptime,
        )
        stored = await self.metrics_repository.create(metric)
        logger.info("system_metrics_stored", metric_id=str(stored.id), hostname=data.hostname)
        return stored

    async def get_latest_system_metrics(self) -> SystemMetric:
        """Retrieves the most recent system metrics record from repository."""
        metrics_list = await self.metrics_repository.list(skip=0, limit=1)
        if not metrics_list:
            logger.warning("latest_system_metrics_not_found")
            raise MetricNotFoundError("No system metrics recorded.")
        return metrics_list[0]

    async def get_metric_history(self, limit: int = 100) -> List[SystemMetric]:
        """Retrieves historical system metrics records up to specified limit."""
        return await self.metrics_repository.list(skip=0, limit=limit)

    async def get_hostname(self) -> str:
        """Returns the hostname from the latest persisted system metrics record."""
        try:
            latest = await self.get_latest_system_metrics()
            return latest.hostname
        except MetricNotFoundError:
            return "unknown-host"

    async def get_operating_system(self) -> str:
        """Returns the OS name from the latest persisted system metrics record."""
        try:
            latest = await self.get_latest_system_metrics()
            return latest.os_name
        except MetricNotFoundError:
            return "unknown-os"

    async def get_uptime(self) -> float:
        """Returns system uptime in seconds from the latest persisted system metrics record."""
        try:
            latest = await self.get_latest_system_metrics()
            return latest.uptime
        except MetricNotFoundError:
            return 0.0
