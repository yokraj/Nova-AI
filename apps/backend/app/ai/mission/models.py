"""Domain models and Pydantic schemas for the Mission Control Engine.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class MissionState(str, Enum):
    """Lifecycle classification states for autonomous missions."""
    CREATED = "created"
    QUEUED = "queued"
    PLANNING = "planning"
    WORKFLOW_GENERATED = "workflow_generated"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    PAUSED = "paused"
    RESUMED = "resumed"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"

class Mission(BaseModel):
    """Represents a long-running autonomous objective."""
    mission_id: str
    goal: str
    creator: str = "user"
    state: MissionState = MissionState.CREATED
    progress: float = 0.0
    active_workflow_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    participating_agents: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MissionContext(BaseModel):
    """Shared execution context variable store across agents."""
    mission_id: str
    variables: Dict[str, Any] = Field(default_factory=dict)

class MissionCheckpoint(BaseModel):
    """Immutable snapshot of the mission state and context history."""
    checkpoint_id: str
    mission_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    mission_snapshot: Dict[str, Any]
    context_snapshot: Dict[str, Any]

class ProgressReport(BaseModel):
    """Spoken progress summary details."""
    mission_id: str
    percentage: float
    completed_tasks: List[str] = Field(default_factory=list)
    remaining_tasks: List[str] = Field(default_factory=list)
    current_stage: str
    eta_seconds: Optional[float] = None
