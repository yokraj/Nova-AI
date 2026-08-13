"""Pydantic data models, enums, and structures for Autonomous Mission & Workflow Engine.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class MissionState(str, Enum):
    """Enumerate long-running mission execution states."""

    CREATED = "CREATED"
    PLANNING = "PLANNING"
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    RECOVERING = "RECOVERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class WorkflowType(str, Enum):
    """Enumerate supported workflow control flow patterns."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    RETRY = "retry"
    BRANCH = "branch"
    MERGE = "merge"
    RECURRING = "recurring"
    DYNAMIC = "dynamic"


class MissionPriority(str, Enum):
    """Enumerate mission priority levels."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
    BACKGROUND = "BACKGROUND"


class WorkerStatus(str, Enum):
    """Enumerate background worker thread statuses."""

    IDLE = "IDLE"
    WORKING = "WORKING"
    PAUSED = "PAUSED"
    RECOVERING = "RECOVERING"
    STOPPED = "STOPPED"


class TaskItem(BaseModel):
    """Single executable task step in a workflow."""

    task_id: str = Field(default_factory=lambda: f"tsk_{uuid.uuid4().hex[:8]}")
    title: str = Field(..., description="Task title or step description")
    action_type: str = Field("agent_execution")
    subsystem: str = Field("swarm_engine")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    status: str = Field("pending", description="Task status (pending, running, completed, failed, skipped)")
    result: Optional[Any] = Field(None)
    retry_count: int = Field(0)
    requires_approval: bool = Field(False)


class WorkflowDefinition(BaseModel):
    """Structured workflow pipeline containing tasks and control flow rules."""

    workflow_id: str = Field(default_factory=lambda: f"wf_{uuid.uuid4().hex[:8]}")
    name: str = Field(...)
    type: WorkflowType = Field(WorkflowType.SEQUENTIAL)
    tasks: List[TaskItem] = Field(default_factory=list)
    branches: Dict[str, List[str]] = Field(default_factory=dict)
    retry_policy: Dict[str, Any] = Field(default_factory=lambda: {"max_retries": 3, "backoff": 1.5})
    cron_expression: Optional[str] = Field(None, description="Optional cron expression for recurring missions")


class CheckpointData(BaseModel):
    """Persistent state snapshot saved for crash and reboot recovery."""

    checkpoint_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:8]}")
    mission_id: str = Field(...)
    task_id: Optional[str] = Field(None)
    state: MissionState = Field(MissionState.RUNNING)
    variables: Dict[str, Any] = Field(default_factory=dict)
    memory: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    browser_state: Dict[str, Any] = Field(default_factory=dict)
    desktop_state: Dict[str, Any] = Field(default_factory=dict)
    voice_session: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class RecoveryRecord(BaseModel):
    """Audit log record of an automated crash or reboot recovery."""

    recovery_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:8]}")
    mission_id: str = Field(...)
    crash_type: str = Field(..., description="Category (app_crash, browser_crash, plugin_crash, timeout, reboot)")
    root_cause: str = Field(...)
    action_taken: str = Field(...)
    success: bool = Field(True)
    recovered_at: float = Field(default_factory=time.time)


class ApprovalItem(BaseModel):
    """Sensitive action pending user approval."""

    approval_id: str = Field(default_factory=lambda: f"appr_{uuid.uuid4().hex[:8]}")
    mission_id: str = Field(...)
    action_title: str = Field(...)
    amount_or_details: str = Field(...)
    requested_at: float = Field(default_factory=time.time)
    status: str = Field("pending", description="Status (pending, approved, rejected)")
    reason: Optional[str] = Field(None)


class ProgressReport(BaseModel):
    """Real-time progress telemetry for long-running missions."""

    mission_id: str = Field(...)
    percent_complete: float = Field(0.0)
    eta_seconds: float = Field(0.0)
    completed_tasks: int = Field(0)
    remaining_tasks: int = Field(0)
    failures: int = Field(0)
    retries: int = Field(0)
    status_summary: str = Field("")


class NotificationMessage(BaseModel):
    """Multi-channel notification payload."""

    notification_id: str = Field(default_factory=lambda: f"notif_{uuid.uuid4().hex[:8]}")
    channel: str = Field("voice", description="Channel (voice, desktop, email, log)")
    title: str = Field(...)
    body: str = Field(...)
    priority: MissionPriority = Field(MissionPriority.NORMAL)
    timestamp: float = Field(default_factory=time.time)


class WorkflowTemplate(BaseModel):
    """Pre-packaged reusable mission template."""

    template_id: str = Field(...)
    name: str = Field(...)
    category: str = Field(...)
    description: str = Field(...)
    workflow_definition: WorkflowDefinition = Field(...)


class MissionRecord(BaseModel):
    """Complete long-running mission record."""

    mission_id: str = Field(default_factory=lambda: f"msn_{uuid.uuid4().hex[:8]}")
    name: str = Field(...)
    goal: str = Field(...)
    state: MissionState = Field(MissionState.CREATED)
    priority: MissionPriority = Field(MissionPriority.NORMAL)
    workflow: WorkflowDefinition = Field(...)
    current_task_index: int = Field(0)
    checkpoints_count: int = Field(0)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class MissionMetrics(BaseModel):
    """Telemetry collector metrics model."""

    total_missions: int = Field(0)
    active_missions: int = Field(0)
    completed_missions: int = Field(0)
    failed_missions: int = Field(0)
    recoveries_succeeded: int = Field(0)
    avg_duration_seconds: float = Field(0.0)
    timestamp: float = Field(default_factory=time.time)


class MissionHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    runtime_state: MissionState = Field(MissionState.RUNNING)
    active_workers_count: int = Field(1)
    queue_length: int = Field(0)
    timestamp: float = Field(default_factory=time.time)
