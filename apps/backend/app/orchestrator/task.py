"""AgentTask schema modeling planned step contexts.
"""

from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field


class AgentTask(BaseModel):
    """Represents a scheduled step in the orchestration plan."""

    task_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique task identifier.")
    agent_name: str = Field(..., description="Target agent name.")
    prompt: str = Field(..., description="Task instructions.")
    status: str = Field("pending", description="Task status (pending, running, completed, failed).")
    result: Optional[Dict[str, Any]] = Field(None, description="Output result of task execution.")
