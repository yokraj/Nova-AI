"""ExecutionContext tracking active task execution metadata parameters.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field


class ExecutionContext(BaseModel):
    """Context detail tracking active execution parameters."""

    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    request_id: Optional[uuid.UUID] = None
    user_id: str = Field("user")
    conversation_id: Optional[uuid.UUID] = None
    agent_name: str = Field(...)
    task_name: str = Field(...)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
