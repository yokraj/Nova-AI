"""SoftwareEngineerSession class representing agent workspace sessions.
"""

from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel, Field

from app.agents.software_engineer.memory import SoftwareEngineerMemory
from app.agents.software_engineer.result import SoftwareEngineerResult
from app.agents.software_engineer.task import SoftwareEngineerTask


class SoftwareEngineerSession(BaseModel):
    """Tracks workspace paths, memories, active subtasks, and execution runs logs."""

    workspace: str = Field("", description="Workspace root path.")
    memory: SoftwareEngineerMemory = Field(default_factory=SoftwareEngineerMemory)
    active_tasks: List[SoftwareEngineerTask] = Field(default_factory=list)
    execution_history: List[SoftwareEngineerResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        """Updates the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)
