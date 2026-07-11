"""HealthStatus schema defining metrics telemetry of the SDK execution runtime.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    """Real-time health telemetry representation for Agent SDK instances."""

    healthy: bool = Field(True, description="Uptime status indicator.")
    uptime: float = Field(0.0, description="Uptime in seconds.")
    last_execution: Optional[datetime] = Field(None, description="Timestamp of last execution run.")
    error_count: int = Field(0, description="Accumulated number of execution failures.")
