"""Health Service Module.

Provides component health diagnostic recording, history tracking, status queries,
and overall health score computation over stored HealthRecords.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.dashboard.exceptions import HealthRecordNotFoundError
from app.dashboard.repositories import HealthRepository
from app.dashboard.schemas import HealthRecordCreate
from app.database.models.dashboard import HealthRecord
from app.database.models.enums import HealthStatus

logger = structlog.get_logger(__name__)


class HealthService:
    """Service layer for system health diagnostic persistence and calculations."""

    def __init__(self, repository: HealthRepository) -> None:
        self.repository = repository
        logger.info("health_service_initialized")

    async def record_health(self, data: HealthRecordCreate) -> HealthRecord:
        """Records a new component health check result into repository."""
        record = HealthRecord(
            snapshot_id=data.snapshot_id,
            timestamp=data.timestamp,
            component=data.component,
            status=data.status.value if hasattr(data.status, "value") else str(data.status),
            latency=data.latency,
            response_time=data.response_time,
            details=data.details,
        )
        stored = await self.repository.create(record)
        logger.info("health_record_created", component=data.component, status=stored.status)
        return stored

    async def get_health_history(self, limit: int = 100) -> List[HealthRecord]:
        """Retrieves historical component health diagnostic records."""
        return await self.repository.list(skip=0, limit=limit)

    async def get_component_health(self, component: str) -> List[HealthRecord]:
        """Retrieves health records for a specific component name."""
        all_records = await self.get_health_history(limit=200)
        filtered = [r for r in all_records if r.component == component]
        if not filtered:
            logger.warning("component_health_not_found", component=component)
            raise HealthRecordNotFoundError(component)
        return filtered

    async def get_health_status(self) -> Dict[str, Any]:
        """Returns overview status of all components based on latest health records."""
        records = await self.get_health_history(limit=100)
        latest_by_component: Dict[str, HealthRecord] = {}
        for r in records:
            if r.component not in latest_by_component:
                latest_by_component[r.component] = r

        unhealthy = [c for c, r in latest_by_component.items() if r.status != HealthStatus.HEALTHY.value]
        is_overall_healthy = len(unhealthy) == 0

        return {
            "is_healthy": is_overall_healthy,
            "score": await self.calculate_health_score(),
            "component_count": len(latest_by_component),
            "unhealthy_components": unhealthy,
            "components": {
                comp: {"status": r.status, "latency": r.latency, "response_time": r.response_time}
                for comp, r in latest_by_component.items()
            },
        }

    async def calculate_health_score(self) -> float:
        """Calculates normalized health score between 0.0 and 1.0."""
        records = await self.get_health_history(limit=50)
        if not records:
            return 1.0

        healthy_count = len([r for r in records if r.status == HealthStatus.HEALTHY.value])
        return round(healthy_count / len(records), 2)
