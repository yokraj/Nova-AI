"""Mission Runtime configuration settings and schemas for Nova Autonomous Mission & Workflow Engine.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class MissionRuntimeConfiguration(BaseModel):
    """Configuration schema for Autonomous Mission Runtime engine."""

    auto_checkpoint_interval_seconds: int = Field(30, description="Interval between automated mission state checkpoints")
    max_background_workers: int = Field(5, description="Maximum concurrent background mission worker threads")
    max_retry_attempts: int = Field(5, description="Maximum automated recovery attempts for crashed steps")
    checkpoint_storage_path: str = Field("./data/checkpoints", description="Path for persistent mission checkpoint storage")
    enable_voice_notifications: bool = Field(True, description="Enables voice progress updates for long-running missions")
    enable_desktop_notifications: bool = Field(True, description="Enables OS desktop notifications for approval & completion")
    default_mission_timeout_hours: float = Field(168.0, description="Default mission timeout (168 hours = 7 days)")
    telemetry_enabled: bool = Field(True, description="Collect mission runtime metrics and event traces")
    cache_ttl_seconds: int = Field(3600, description="Cache expiration duration in seconds")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom settings")
