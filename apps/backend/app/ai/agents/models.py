"""Pydantic V2 data models and schemas for Universal Agent Workforce & Autonomous AI Company.
"""

from enum import Enum, EnumMeta
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict
import time
import uuid


class AgentCapability(BaseModel):
    """Specification of an agent capability."""
    name: str
    description: str = ""

    def __str__(self) -> str:
        return self.name


class AgentDivision(str, Enum):
    """Enumerate the 9 specialized divisions of Nova Autonomous AI Company."""

    EXECUTIVE = "EXECUTIVE"
    ENGINEERING = "ENGINEERING"
    RESEARCH = "RESEARCH"
    CREATIVE = "CREATIVE"
    BUSINESS = "BUSINESS"
    AUTOMATION = "AUTOMATION"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    QUALITY = "QUALITY"
    SECURITY = "SECURITY"


class AgentStatusRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    health: str = "HEALTHY"
    uptime_seconds: float = 0.0
    active_tasks_count: int = 0
    errors_count: int = 0


class AgentStatusMeta(EnumMeta):
    def __call__(cls, *args, **kwargs):
        if kwargs:
            return AgentStatusRecord(**kwargs)
        return super().__call__(*args)


class AgentStatus(str, Enum, metaclass=AgentStatusMeta):
    """Operational status of an AI agent."""

    IDLE = "IDLE"
    ASSIGNED = "ASSIGNED"
    EXECUTING = "EXECUTING"
    REVIEWING = "REVIEWING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskPriority(str, Enum):
    """Task execution priority levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskStatus(str, Enum):
    """Lifecycle status of a delegated task node."""

    PENDING = "PENDING"
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentBlueprint(BaseModel):
    """Blueprint specification for a specialized agent within a division."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    agent_id: str = Field(default="", alias="id")
    name: str = Field("Specialized Agent")
    division: AgentDivision = Field(AgentDivision.ENGINEERING)
    role_description: str = Field("Autonomous agent executing specialized domain tasks.")
    skills: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    status: AgentStatus = Field(AgentStatus.IDLE)

    @property
    def id(self) -> str:
        return self.agent_id



class TaskNode(BaseModel):
    """Individual task node within a mission execution DAG."""

    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    title: str = Field(...)
    description: str = Field(...)
    assigned_division: AgentDivision = Field(...)
    assigned_agent_id: Optional[str] = Field(None)
    dependencies: List[str] = Field(default_factory=list)
    priority: TaskPriority = Field(TaskPriority.MEDIUM)
    status: TaskStatus = Field(TaskStatus.PENDING)
    output: Optional[Any] = Field(None)
    created_at: float = Field(default_factory=time.time)


class MissionPlanDAG(BaseModel):
    """Complete hierarchical mission plan execution DAG."""

    mission_id: str = Field(default_factory=lambda: f"msn_{uuid.uuid4().hex[:8]}")
    goal: str = Field(...)
    task_nodes: List[TaskNode] = Field(default_factory=list)
    created_by: str = Field("ExecutiveDivision:CEOAgent")
    status: TaskStatus = Field(TaskStatus.PENDING)
    progress_percent: float = Field(0.0)


class PeerReviewRequest(BaseModel):
    """Peer review evaluation request payload."""

    review_id: str = Field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:8]}")
    task_id: str = Field(...)
    author_agent_id: str = Field(...)
    content_to_review: Any = Field(...)
    required_reviewers: List[str] = Field(default_factory=lambda: ["CodeReviewAgent", "SecurityAuditAgent", "QAAgent"])


class PeerReviewResult(BaseModel):
    """Peer review evaluation result."""

    review_id: str = Field(...)
    task_id: str = Field(...)
    approved: bool = Field(True)
    overall_quality_score: float = Field(0.95)
    reviewer_comments: Dict[str, str] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class AgentMessage(BaseModel):
    """Inter-agent communication bus message."""

    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    sender_agent_id: str = Field(...)
    recipient_agent_id: str = Field("BROADCAST")
    event_type: str = Field(...)
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class SharedMemoryItem(BaseModel):
    """Shared agent memory item."""

    key: str = Field(...)
    category: str = Field("general")
    value: Any = Field(...)
    author: str = Field(...)
    timestamp: float = Field(default_factory=time.time)


class AgentLearningRecord(BaseModel):
    """Persisted learning record for successful workflow patterns."""

    record_id: str = Field(default_factory=lambda: f"lrn_{uuid.uuid4().hex[:8]}")
    pattern_name: str = Field(...)
    successful_steps: List[str] = Field(default_factory=list)
    optimizations: Dict[str, Any] = Field(default_factory=dict)


class WorkforceTelemetry(BaseModel):
    """Workforce performance telemetry stats."""

    total_agents_count: int = Field(67)
    active_agents_count: int = Field(12)
    total_missions_completed: int = Field(0)
    total_tasks_executed: int = Field(0)
    peer_reviews_passed: int = Field(0)
    average_task_latency_ms: float = Field(120.0)


class WorkforceHealth(BaseModel):
    """Overall health snapshot of Nova Autonomous AI Company."""

    is_healthy: bool = Field(True)
    status: str = Field("HEALTHY")
    divisions_count: int = Field(9)
    total_registered_agents: int = Field(67)
    active_bus_listeners: int = Field(15)
    telemetry: WorkforceTelemetry = Field(default_factory=WorkforceTelemetry)


class AgentDescriptor(BaseModel):
    model_config = ConfigDict(extra="allow")
    class_path: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)


class AgentRegistration(BaseModel):
    model_config = ConfigDict(extra="allow")
    registration_id: str
    descriptor: Any
    metadata: Any


class AgentResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    execution_id: str = Field(default="")
    status: str = Field(default="success")
    data: Optional[Any] = Field(default=None)
    duration_ms: float = Field(default=0.0)
    error_message: Optional[str] = Field(default=None)


class AgentHeartbeat(BaseModel):
    model_config = ConfigDict(extra="allow")
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    state: str = "READY"
    uptime: float = 0.0
    memory_usage_bytes: int = 0
    execution_count: int = 0
    active_task: Optional[str] = None


class AgentState(BaseModel):
    model_config = ConfigDict(extra="allow")
    value: str = "IDLE"
    progress: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class AgentInfo(BaseModel):
    model_config = ConfigDict(extra="allow")
    metadata: Any = None
    state: Any = None
    status: Any = None
    active_task: Optional[str] = None


AgentMetadata = AgentBlueprint
AgentContext = TaskNode






