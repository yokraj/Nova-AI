"""ExecutionState schema tracking execution pipeline stages.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ExecutionState(BaseModel):
    """Tracks running execution tasks lists inside orchestrator runs."""

    pending: List[Dict[str, Any]] = Field(default_factory=list, description="List of pending tasks.")
    running: List[Dict[str, Any]] = Field(default_factory=list, description="List of currently executing tasks.")
    completed: List[Dict[str, Any]] = Field(default_factory=list, description="List of successfully completed tasks.")
    failed: List[Dict[str, Any]] = Field(default_factory=list, description="List of failed tasks.")
