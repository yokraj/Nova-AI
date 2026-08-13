"""Collaboration Context storing global shared states and generated artifacts.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field

class CollaborationContext(BaseModel):
    """Stores shared goal metrics, completed steps, and shared artifacts map."""
    project_goal: str
    current_status: str = "initialized"
    completed_tasks: List[str] = Field(default_factory=list)
    shared_artifacts: Dict[str, Any] = Field(default_factory=dict)
    discussion_history: List[str] = Field(default_factory=list)

    def add_shared_artifact(self, key: str, value: Any) -> None:
        """Stores custom artifact into shared pool."""
        self.shared_artifacts[key] = value

    def add_discussion_log(self, entry: str) -> None:
        """Appends log text entry to history logs."""
        self.discussion_history.append(entry)
