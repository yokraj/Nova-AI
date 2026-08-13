"""Analytics Engine Exception Hierarchy Module.

Defines custom domain exception classes for metric aggregations, time-series querying,
trend calculations, anomaly detection, report generation, and retention cleanup.
"""


class AnalyticsEngineError(Exception):
    """Base exception class for all Analytics Engine failures."""

    def __init__(self, message: str = "Analytics engine error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class AggregationError(AnalyticsEngineError):
    """Raised when aggregating raw metrics across time buckets fails."""

    def __init__(self, metric_name: str, detail: str) -> None:
        super().__init__(f"Aggregation failed for metric '{metric_name}': {detail}")


class TrendAnalysisError(AnalyticsEngineError):
    """Raised when computing trend lines or growth rates fails."""

    def __init__(self, metric_name: str, detail: str) -> None:
        super().__init__(f"Trend analysis failed for '{metric_name}': {detail}")


class ReportGenerationError(AnalyticsEngineError):
    """Raised when generating a structured analytics report fails."""

    def __init__(self, report_type: str, detail: str) -> None:
        super().__init__(f"Failed to generate report '{report_type}': {detail}")


class KPIError(AnalyticsEngineError):
    """Raised when computing KPI values or benchmarks fails."""

    def __init__(self, kpi_name: str, detail: str) -> None:
        super().__init__(f"KPI calculation failed for '{kpi_name}': {detail}")


class InsightError(AnalyticsEngineError):
    """Raised when evaluating diagnostic rules for insight generation fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Insight generation error: {detail}")


class RetentionError(AnalyticsEngineError):
    """Raised when executing analytics retention cleanup or purging fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Retention cleanup error: {detail}")


class AnomalyDetectionError(AnalyticsEngineError):
    """Raised when evaluating statistical anomaly baselines fails."""

    def __init__(self, metric_name: str, detail: str) -> None:
        super().__init__(f"Anomaly detection error for '{metric_name}': {detail}")
