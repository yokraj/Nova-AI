"""Configuration options for enabling/disabling observability channels.
"""

from pydantic import BaseModel, Field


class ObservabilityConfiguration(BaseModel):
    """Configuration options for enabling/disabling observability channels."""

    enable_logging: bool = Field(True)
    enable_metrics: bool = Field(True)
    enable_tracing: bool = Field(True)
    enable_profiling: bool = Field(True)
    enable_telemetry: bool = Field(True)
    enable_audit: bool = Field(True)
    enable_events: bool = Field(True)
    log_level: str = Field("INFO")
