"""Memory Statistics Module.

Tracks memory_count, workspace_count, project_count, compression_ratio,
retrieval_count, search_latency_ms, and storage_usage_bytes metrics.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import structlog

from app.memory.repository import MemoryRepository
from app.memory.schemas import MemoryStatisticsSchema

logger = structlog.get_logger(__name__)


class MemoryStatisticsTracker:
    """Enterprise Memory Platform Metrics & Telemetry Tracker."""

    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository
        self._retrieval_count: int = 0
        self._last_latency_ms: float = 2.45
        self._compression_ratio: float = 1.0
        logger.info("memory_statistics_tracker_initialized")

    def record_retrieval(self, latency_ms: float = 1.5) -> None:
        """Records a retrieval operation and latency measurement."""
        self._retrieval_count += 1
        self._last_latency_ms = round(latency_ms, 2)

    def record_compression(self, ratio: float) -> None:
        """Updates cumulative memory compression ratio."""
        self._compression_ratio = round(ratio, 2)

    async def get_statistics(self) -> MemoryStatisticsSchema:
        """Computes and returns aggregated platform statistics telemetry."""
        counts = await self.repository.get_statistics_counts()
        storage_bytes = counts["memory_count"] * 1024  # Estimated storage usage

        return MemoryStatisticsSchema(
            memory_count=counts["memory_count"],
            workspace_count=counts["workspace_count"],
            project_count=counts["project_count"],
            compression_ratio=self._compression_ratio,
            retrieval_count=self._retrieval_count,
            search_latency_ms=self._last_latency_ms,
            storage_usage_bytes=storage_bytes,
            timestamp=datetime.now(timezone.utc),
        )
