"""Telemetry and metrics collector for Universal Knowledge, Research & Reasoning Engine.
"""

import time
from app.ai.research.models import ResearchMetrics


class ResearchMetricsTracker:
    """Collects research telemetry metrics and execution timing."""

    def __init__(self) -> None:
        self._queries = 0
        self._sources = 0
        self._claims = 0
        self._reports = 0
        self._total_time = 0.0

    def record_research(self, sources_count: int, claims_count: int, elapsed_sec: float) -> None:
        """Records telemetry metrics for completed research session."""
        self._queries += 1
        self._sources += sources_count
        self._claims += claims_count
        self._reports += 1
        self._total_time += elapsed_sec

    def get_metrics(self) -> ResearchMetrics:
        """Returns current ResearchMetrics snapshot."""
        avg_t = (self._total_time / self._queries) if self._queries > 0 else 0.0
        return ResearchMetrics(
            queries_processed=self._queries,
            sources_ingested=self._sources,
            claims_verified=self._claims,
            reports_generated=self._reports,
            avg_time_sec=avg_t,
            timestamp=time.time(),
        )
