"""Configuration settings profiles for the Mission Control Engine.
"""

from pydantic_settings import BaseSettings
from pydantic import Field

class MissionConfiguration(BaseSettings):
    """Configuration settings for mission queues, concurrency, and telemetry limits."""

    max_concurrent_missions: int = Field(default=3, description="Max concurrent executing missions")
    mission_timeout_seconds: int = Field(default=86400, description="Max duration in seconds for a mission (24 hours)")
    checkpoint_interval_seconds: int = Field(default=600, description="Interval in seconds for saving mission checkpoints")
    storage_path: str = Field(default="./data/missions", description="Local directory path to save serialized mission files")

    class Config:
        env_prefix = "NOVA_MISSION_"
        case_sensitive = False
