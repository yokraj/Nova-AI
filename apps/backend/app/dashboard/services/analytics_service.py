"""Analytics Service Module.

Provides analytics metric recording, historical metric query interfaces, dashboard statistics,
and time-period aggregation over stored analytics records.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.dashboard.exceptions import MetricNotFoundError
from app.dashboard.repositories import AnalyticsRepository
from app.dashboard.schemas import AnalyticsRecordCreate
from app.database.models.dashboard import AnalyticsRecord

logger = structlog.get_logger(__name__)


class AnalyticsService:
    """Service layer for analytics metrics ingestion and statistical aggregation."""

    def __init__(self, repository: AnalyticsRepository) -> None:
        self.repository = repository
        logger.info("analytics_service_initialized")

    async def record_metric(self, data: AnalyticsRecordCreate) -> AnalyticsRecord:
        """Records an analytics metric sample into repository."""
        record = AnalyticsRecord(
            snapshot_id=data.snapshot_id,
            metric_name=data.metric_name,
            metric_value=data.metric_value,
            metric_type=data.metric_type,
            aggregation_period=data.aggregation_period,
            labels=data.labels,
        )
        stored = await self.repository.create(record)
        logger.info("analytics_metric_recorded", metric_name=data.metric_name, value=data.metric_value)
        return stored

    async def get_metric_history(
        self, metric_name: str, limit: int = 100
    ) -> List[AnalyticsRecord]:
        """Retrieves historical analytics records matching metric_name."""
        all_records = await self.repository.list(skip=0, limit=limit * 2)
        filtered = [r for r in all_records if r.metric_name == metric_name]
        return filtered[:limit]

    async def get_metrics(self, metric_name: str) -> List[AnalyticsRecord]:
        """Retrieves latest metrics for a given metric_name."""
        return await self.get_metric_history(metric_name=metric_name, limit=50)

    async def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Computes summary statistics across stored analytics records."""
        records = await self.repository.list(skip=0, limit=500)
        total_requests = len(records)
        values = [r.metric_value for r in records]
        avg_val = sum(values) / len(values) if values else 0.0

        return {
            "total_records": total_requests,
            "average_metric_value": avg_val,
            "max_metric_value": max(values) if values else 0.0,
            "min_metric_value": min(values) if values else 0.0,
        }

    async def aggregate_metrics(
        self, metric_name: str, aggregation_period: str = "hourly"
    ) -> Dict[str, Any]:
        """Calculates aggregated sum, mean, min, max for metric_name over period."""
        history = await self.get_metric_history(metric_name=metric_name, limit=500)
        values = [r.metric_value for r in history if r.aggregation_period == aggregation_period or not aggregation_period]

        if not values:
            logger.warning("aggregate_metrics_empty", metric_name=metric_name)
            return {
                "metric_name": metric_name,
                "aggregation_period": aggregation_period,
                "count": 0,
                "sum": 0.0,
                "mean": 0.0,
                "min": 0.0,
                "max": 0.0,
            }

        return {
            "metric_name": metric_name,
            "aggregation_period": aggregation_period,
            "count": len(values),
            "sum": sum(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }
