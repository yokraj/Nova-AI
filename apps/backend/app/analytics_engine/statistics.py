"""Analytics Statistics Module.

Tracks engine telemetry including aggregation run counts, report counts,
detected anomalies, computed KPIs, generated insights, and query processing latencies.
"""

from typing import Any, Dict
import structlog

logger = structlog.get_logger(__name__)


class AnalyticsStatistics:
    """Telemetry performance statistics tracker for Analytics Engine."""

    def __init__(self) -> None:
        self.aggregation_runs: int = 0
        self.reports_generated: int = 0
        self.anomalies_detected: int = 0
        self.kpis_generated: int = 0
        self.insights_generated: int = 0
        self.cleanup_runs: int = 0
        self.total_processing_time_ms: float = 0.0
        self.total_query_time_ms: float = 0.0
        self.query_count: int = 0

        logger.info("analytics_statistics_initialized")

    def record_aggregation(self, duration_ms: float = 0.0) -> None:
        self.aggregation_runs += 1
        self.total_processing_time_ms += duration_ms

    def record_report(self) -> None:
        self.reports_generated += 1

    def record_anomalies(self, count: int = 1) -> None:
        self.anomalies_detected += count

    def record_kpis(self) -> None:
        self.kpis_generated += 1

    def record_insights(self, count: int = 1) -> None:
        self.insights_generated += count

    def record_cleanup(self) -> None:
        self.cleanup_runs += 1

    def record_query(self, duration_ms: float) -> None:
        self.query_count += 1
        self.total_query_time_ms += duration_ms

    def get_summary(self) -> Dict[str, Any]:
        """Returns analytics engine performance summary dictionary."""
        avg_processing = (
            (self.total_processing_time_ms / self.aggregation_runs)
            if self.aggregation_runs > 0
            else 0.0
        )
        avg_query = (
            (self.total_query_time_ms / self.query_count)
            if self.query_count > 0
            else 0.0
        )

        return {
            "aggregation_runs": self.aggregation_runs,
            "reports_generated": self.reports_generated,
            "anomalies_detected": self.anomalies_detected,
            "kpis_generated": self.kpis_generated,
            "insights_generated": self.insights_generated,
            "cleanup_runs": self.cleanup_runs,
            "average_processing_time_ms": round(avg_processing, 2),
            "average_query_time_ms": round(avg_query, 2),
        }

    def reset(self) -> None:
        """Resets all telemetry counters."""
        self.aggregation_runs = 0
        self.reports_generated = 0
        self.anomalies_detected = 0
        self.kpis_generated = 0
        self.insights_generated = 0
        self.cleanup_runs = 0
        self.total_processing_time_ms = 0.0
        self.total_query_time_ms = 0.0
        self.query_count = 0
