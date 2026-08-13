"""Domain models and data schemas for the Autonomous Skill Execution Runtime."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ExecutionState(str, Enum):
    """Overall execution state of a mission or task."""

    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    ROLLBACK_IN_PROGRESS = "rollback_in_progress"
    ROLLED_BACK = "rolled_back"


class StepStatus(str, Enum):
    """Lifecycle status of an individual execution step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRIED = "retried"
    ROLLED_BACK = "rolled_back"


class PriorityLevel(int, Enum):
    """Priority level for queued execution tasks (higher integer = higher priority)."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


# ---------------------------------------------------------------------------
# Domain Models
# ---------------------------------------------------------------------------

class ExecutionStep(BaseModel):
    """An atomic execution step within a mission plan."""

    step_id: str = Field(default_factory=lambda: f"step_{uuid4().hex[:8]}")
    name: str
    plugin_id: str
    capability: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    is_transactional: bool = False
    rollback_capability: Optional[str] = None
    rollback_parameters: Dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False
    output: Optional[Any] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0


class MissionExecutionPlan(BaseModel):
    """Complete execution plan for a multi-step mission."""

    mission_id: str
    goal: str
    steps: List[ExecutionStep] = Field(default_factory=list)
    priority: PriorityLevel = PriorityLevel.NORMAL
    state: ExecutionState = ExecutionState.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    agents_involved: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CheckpointData(BaseModel):
    """Persisted snapshot of a mission's state for checkpoint/resume."""

    checkpoint_id: str = Field(default_factory=lambda: f"chk_{uuid4().hex[:10]}")
    mission_id: str
    goal: str
    completed_step_ids: List[str] = Field(default_factory=list)
    step_outputs: Dict[str, Any] = Field(default_factory=dict)
    shared_context: Dict[str, Any] = Field(default_factory=dict)
    state: ExecutionState = ExecutionState.PAUSED
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TransactionRecord(BaseModel):
    """Audit record for a transactional execution block."""

    transaction_id: str = Field(default_factory=lambda: f"tx_{uuid4().hex[:10]}")
    mission_id: str
    executed_steps: List[ExecutionStep] = Field(default_factory=list)
    committed: bool = False
    rolled_back: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ResourceSnapshot(BaseModel):
    """System resource usage snapshot."""

    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    gpu_percent: Optional[float] = None
    disk_percent: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExecutionMetrics(BaseModel):
    """Telemetry metrics snapshot for the execution runtime."""

    total_missions: int = 0
    completed_missions: int = 0
    failed_missions: int = 0
    cancelled_missions: int = 0
    success_rate: float = 0.0
    average_mission_duration_seconds: float = 0.0
    total_steps_executed: int = 0
    total_retries: int = 0
    total_rollbacks: int = 0
    human_approvals_requested: int = 0


class ExecutionHealth(BaseModel):
    """Composite health report for the execution runtime."""

    status: str = "healthy"
    components: Dict[str, str] = Field(default_factory=dict)
    active_missions_count: int = 0
    queued_tasks_count: int = 0
