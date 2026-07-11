"""Health status and metrics tracking for registered agents.
"""

from datetime import datetime, UTC
from typing import Optional
from pydantic import BaseModel, Field
from app.agents.registry.status import AgentStatus


class HealthReport(BaseModel):
    """Health status and telemetry metrics report for an agent."""

    status: AgentStatus = Field(AgentStatus.REGISTERED, description="Current execution status.")
    uptime: float = Field(0.0, description="Uptime duration in seconds.")
    last_execution: Optional[datetime] = Field(None, description="Timestamp of last execution run.")
    average_latency: float = Field(0.0, description="Average response duration in seconds.")
    error_count: int = Field(0, description="Number of execution errors encountered.")


class AgentHealth(HealthReport):
    """Health status and telemetry metrics for a registered agent."""

    pass

