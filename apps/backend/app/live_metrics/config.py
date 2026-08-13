"""Live Metrics Engine Configuration Module.

Defines configuration DTOs and parameters for real-time metric sampling,
rate limiting, change detection thresholds, and snapshot retention limits.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class LiveMetricsConfig(BaseModel):
    """Configuration DTO for the Live Metrics Engine."""

    metrics_interval: float = Field(default=1.0, ge=0.1, le=60.0, description="Collection interval in seconds")
    heartbeat_interval: float = Field(default=30.0, ge=1.0, le=300.0, description="Heartbeat interval in seconds")
    buffer_size: int = Field(default=100, ge=10, le=5000, description="Maximum metric event buffer capacity")
    publish_rate: float = Field(default=10.0, ge=0.5, le=100.0, description="Max updates per second per channel")
    change_threshold: float = Field(default=0.01, ge=0.0, le=0.5, description="Min percentage change delta to publish")
    snapshot_retention: int = Field(default=50, ge=5, le=1000, description="Max historical snapshots to retain in memory")

    @classmethod
    def from_dashboard_config(cls, db_config: Optional[Any] = None) -> "LiveMetricsConfig":
        """Instantiates LiveMetricsConfig from DashboardConfiguration database model or dict."""
        if not db_config:
            return cls()

        if isinstance(db_config, dict):
            return cls(
                metrics_interval=float(db_config.get("metrics_interval", 1.0)),
                heartbeat_interval=float(db_config.get("heartbeat_interval", 30.0)),
                buffer_size=int(db_config.get("buffer_size", 100)),
                publish_rate=float(db_config.get("publish_rate", 10.0)),
                change_threshold=float(db_config.get("change_threshold", 0.01)),
                snapshot_retention=int(db_config.get("snapshot_retention", 50)),
            )

        return cls(
            metrics_interval=float(getattr(db_config, "metrics_interval", 1.0)),
            heartbeat_interval=float(getattr(db_config, "heartbeat_interval", 30.0)),
            buffer_size=int(getattr(db_config, "buffer_size", 100)),
            publish_rate=float(getattr(db_config, "publish_rate", 10.0)),
            change_threshold=float(getattr(db_config, "change_threshold", 0.01)),
            snapshot_retention=int(getattr(db_config, "snapshot_retention", 50)),
        )
