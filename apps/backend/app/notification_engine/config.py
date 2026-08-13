"""Notification Engine Configuration Module.

Defines configuration DTOs reading parameters from DashboardConfiguration database
models or dictionary options with fallback defaults.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class NotificationConfig(BaseModel):
    """Configuration DTO for the Enterprise Notification Engine."""

    notification_retention_days: int = Field(default=30, ge=1, le=365, description="Days to retain notifications before purge")
    max_notifications: int = Field(default=1000, ge=50, le=100000, description="Max notifications to retain per user/system")
    duplicate_window: int = Field(default=300, ge=5, le=86400, description="Deduplication time window in seconds")
    delivery_retry_limit: int = Field(default=3, ge=0, le=10, description="Max delivery attempt retry limit")
    cleanup_interval: float = Field(default=3600.0, ge=60.0, le=86400.0, description="Background cleanup interval in seconds")
    priority_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "cpu_high": 85.0,
            "cpu_urgent": 95.0,
            "memory_high": 85.0,
            "memory_urgent": 95.0,
            "disk_high": 85.0,
            "disk_urgent": 95.0,
            "gpu_high": 85.0,
            "gpu_urgent": 95.0,
        },
        description="Threshold mappings for priority calculation",
    )

    @classmethod
    def from_dashboard_config(cls, db_config: Optional[Any] = None) -> "NotificationConfig":
        """Instantiates NotificationConfig from DashboardConfiguration model or dict."""
        if not db_config:
            return cls()

        if isinstance(db_config, dict):
            return cls(
                notification_retention_days=int(db_config.get("retention_days", 30)),
                max_notifications=int(db_config.get("max_notifications", 1000)),
                duplicate_window=int(db_config.get("duplicate_window", 300)),
                delivery_retry_limit=int(db_config.get("delivery_retry_limit", 3)),
                cleanup_interval=float(db_config.get("cleanup_interval", 3600.0)),
            )

        return cls(
            notification_retention_days=int(getattr(db_config, "retention_days", 30)),
            max_notifications=int(getattr(db_config, "max_notifications", 1000)),
            duplicate_window=int(getattr(db_config, "duplicate_window", 300)),
            delivery_retry_limit=int(getattr(db_config, "delivery_retry_limit", 3)),
            cleanup_interval=float(getattr(db_config, "cleanup_interval", 3600.0)),
        )
