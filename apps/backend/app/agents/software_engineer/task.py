"""SoftwareEngineerTask mapping agent subtasks.
"""

from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class SoftwareEngineerTask(BaseModel):
    """Represent an individual execution task inside the session tracking list."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str = Field(..., description="Short task title.")
    description: str = Field("", description="Detailed instructions.")
    priority: str = Field("normal", description="Task priority (low, normal, high, critical).")
    status: str = Field("pending", description="Task status (pending, in_progress, completed, failed).")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def update_status(self, new_status: str) -> None:
        """Updates task status and refreshes modified timestamp."""
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)
