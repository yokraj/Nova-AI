"""AgentJob schemas tracking task configurations.
"""

from datetime import datetime, UTC
from typing import Optional
import uuid
from pydantic import BaseModel, Field
from app.agents.bus.request import AgentRequest
from app.agents.scheduler.priority import Priority
from app.agents.scheduler.status import JobStatus
from app.agents.scheduler.retry_policy import RetryPolicy


class AgentJob(BaseModel):
    """Represents a scheduled task to be executed by an agent."""

    job_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique job identifier.")
    agent_id: uuid.UUID = Field(..., description="Target agent identifier.")
    request: AgentRequest = Field(..., description="AgentRequest payload details.")
    priority: Priority = Field(Priority.NORMAL, description="Job priority status.")
    scheduled_time: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time when the job should be executed.")
    timeout: Optional[float] = Field(None, description="Timeout duration in seconds.")
    retry_count: int = Field(0, description="Number of times the job has been retried.")
    status: JobStatus = Field(JobStatus.PENDING, description="Current status of the job.")
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy, description="Retry configuration policy.")
