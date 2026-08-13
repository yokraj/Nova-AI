"""Analytics Engine Configuration Module.

Defines configuration parameters for analytics data retention, aggregation intervals,
anomaly detection thresholds, report generation frequencies, and cleanup intervals.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AnalyticsConfig(BaseModel):
    """Configuration DTO for the Enterprise Analytics Engine."""

    analytics_retention_days: int = Field(default=90, ge=1, le=3650, description="Days to retain historical analytics records")
    aggregation_interval: float = Field(default=60.0, ge=5.0, le=3600.0, description="Metrics aggregation interval in seconds")
    report_interval: float = Field(default=3600.0, ge=60.0, le=86400.0, description="Scheduled report generation interval in seconds")
    anomaly_threshold: float = Field(default=2.0, ge=0.5, le=5.0, description="Statistical z-score threshold for anomaly detection")
    insight_threshold: float = Field(default=0.8, ge=0.1, le=1.0, description="Confidence threshold for generating insight alerts")
    cleanup_interval: float = Field(default=86400.0, ge=3600.0, le=604800.0, description="Background retention cleanup interval in seconds")

    @classmethod
    def from_dashboard_config(cls, db_config: Optional[Any] = None) -> "AnalyticsConfig":
        """Instantiates AnalyticsConfig from DashboardConfiguration model or dict."""
        if not db_config:
            return cls()

        if isinstance(db_config, dict):
            return cls(
                analytics_retention_days=int(db_config.get("retention_days", 90)),
                aggregation_interval=float(db_config.get("aggregation_interval", 60.0)),
                report_interval=float(db_config.get("report_interval", 3600.0)),
                anomaly_threshold=float(db_config.get("anomaly_threshold", 2.0)),
                insight_threshold=float(db_config.get("insight_threshold", 0.8)),
                cleanup_interval=float(db_config.get("cleanup_interval", 86400.0)),
            )

        return cls(
            analytics_retention_days=int(getattr(db_config, "retention_days", 90)),
            aggregation_interval=float(getattr(db_config, "aggregation_interval", 60.0)),
            report_interval=float(getattr(db_config, "report_interval", 3600.0)),
            anomaly_threshold=float(getattr(db_config, "anomaly_threshold", 2.0)),
            insight_threshold=float(getattr(db_config, "insight_threshold", 0.8)),
            cleanup_interval=float(getattr(db_config, "cleanup_interval", 86400.0)),
        )
