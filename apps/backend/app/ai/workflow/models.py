"""Domain models and Pydantic schemas for the Workflow Orchestration Engine.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class WorkflowState(str, Enum):
    """Classification states for workflows and step items."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class WorkflowStep(BaseModel):
    """Represents a discrete execution node in a workflow DAG."""
    step_id: str
    title: str
    description: str
    agent_id: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    state: WorkflowState = WorkflowState.PENDING
    dependencies: List[str] = Field(default_factory=list)
    retry_count: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Workflow(BaseModel):
    """Represents a multi-step orchestrated plan workflow."""
    workflow_id: str
    goal: str
    creator: str = "system"
    state: WorkflowState = WorkflowState.PENDING
    steps: Dict[str, WorkflowStep] = Field(default_factory=dict)
    progress: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowContext(BaseModel):
    """Mutable execution context variables store."""
    workflow_id: str
    variables: Dict[str, Any] = Field(default_factory=dict)

class WorkflowCheckpoint(BaseModel):
    """Immutable snapshot of workflow progress state history."""
    checkpoint_id: str
    workflow_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    workflow_snapshot: Dict[str, Any]
    context_snapshot: Dict[str, Any]

class WorkflowArtifact(BaseModel):
    """Output asset or artifact generated during step execution."""
    artifact_id: str
    workflow_id: str
    step_id: str
    name: str
    data: Any
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ApprovalRequest(BaseModel):
    """Human-in-the-loop approval gating request request."""
    approval_id: str
    workflow_id: str
    step_id: str
    action: str
    reason: str
    status: str = "pending"
    requested_at: datetime = Field(default_factory=datetime.utcnow)

class ApprovalResult(BaseModel):
    """Human-in-the-loop gate response resolving request."""
    approval_id: str
    approved: bool
    reviewer: str = "user"
    comments: Optional[str] = None
    resolved_at: datetime = Field(default_factory=datetime.utcnow)
