"""Workflow and context models for Nova AI automation workflows.

Defines schemas, execution states, steps, contexts, and result types.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """Execution status states for workflows and steps."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep(BaseModel):
    """Represents a single task step configuration within a workflow."""

    id: str = Field(..., description="Unique step identifier name.")
    name: str = Field(..., description="Descriptive step display name.")
    capability: str = Field(
        ...,
        description="The provider/system capability needed (e.g. 'text', 'vision').",
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="List of other step IDs this step depends on.",
    )
    input_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Maps context variables keys to step inputs.",
    )
    output_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Maps step results output keys to context variables.",
    )
    retry_limit: int = Field(
        0, ge=0, description="Max failed attempts limit before failing step."
    )
    timeout_seconds: Optional[float] = Field(
        None, gt=0.0, description="Maximum execution timeout limit in seconds."
    )
    status: WorkflowStatus = Field(
        WorkflowStatus.PENDING, description="Current execution state."
    )
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class Workflow(BaseModel):
    """Represents a structured graph of execution steps."""

    id: str = Field(..., description="Unique workflow identifier.")
    name: str = Field(..., description="Workflow title/display name.")
    steps: List[WorkflowStep] = Field(
        ..., description="List of tasks/steps configured."
    )
    status: WorkflowStatus = Field(
        WorkflowStatus.PENDING, description="Current execution state."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional unstructured metadata information.",
    )


class HistoryEntry(BaseModel):
    """Records a single state transition history log details."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event: str = Field(..., description="Description of the event.")
    step_id: Optional[str] = Field(
        None, description="Optional associated step ID."
    )
    details: Optional[Dict[str, Any]] = Field(
        None, description="Optional extra debug metadata details."
    )


class WorkflowContext(BaseModel):
    """Maintains shared execution state variables and transaction history logs."""

    variables: Dict[str, Any] = Field(
        default_factory=dict, description="Variables lookup dictionary."
    )
    history: List[HistoryEntry] = Field(
        default_factory=list, description="State transitions history log."
    )
    is_cancelled: bool = Field(
        False, description="Flag representing cancellation requests."
    )

    def log(
        self,
        event: str,
        step_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Adds a new transaction history event log."""
        self.history.append(
            HistoryEntry(event=event, step_id=step_id, details=details)
        )


class WorkflowResult(BaseModel):
    """Final result container representing workflow execution finishes."""

    workflow_id: str = Field(..., description="Target workflow ID.")
    status: WorkflowStatus = Field(
        ..., description="Final execution lifecycle state."
    )
    variables: Dict[str, Any] = Field(
        ..., description="Snapshot of execution variables."
    )
    history: List[HistoryEntry] = Field(
        ..., description="Completed execution log entries list."
    )
    error_message: Optional[str] = Field(
        None, description="Detailed final error description if failed."
    )
