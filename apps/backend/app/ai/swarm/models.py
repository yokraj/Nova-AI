"""Domain models and data schemas for Multi-Agent Collaboration & Swarm Intelligence."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SwarmState(str, Enum):
    """Overall operational state of a swarm mission."""

    INITIALIZING = "initializing"
    DECOMPOSING = "decomposing"
    ALLOCATING = "allocating"
    EXECUTING = "executing"
    VOTING = "voting"
    CONSENSUS_REACHED = "consensus_reached"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRole(str, Enum):
    """Specialized roles for swarm agents."""

    EXECUTIVE = "executive"
    PLANNER = "planner"
    SOFTWARE_ENGINEER = "software_engineer"
    SECURITY = "security"
    RESEARCH = "research"
    MEMORY = "memory"
    EXECUTION = "execution"
    AUTOMATION = "automation"
    BROWSER = "browser"
    DESKTOP = "desktop"
    SERVICE = "service"
    LEARNING = "learning"
    PERSONAL_ASSISTANT = "personal_assistant"
    AMBIENT = "ambient"
    VISION = "vision"
    VOICE = "voice"


class VotingStrategy(str, Enum):
    """Voting strategies for resolving conflicting agent decisions."""

    MAJORITY = "majority"
    WEIGHTED = "weighted"
    CONFIDENCE = "confidence"
    LEADER = "leader"


class ConsensusType(str, Enum):
    """Consensus outcome classification."""

    UNANIMOUS = "unanimous"
    MAJORITY = "majority"
    WEIGHTED = "weighted"
    LEADER_OVERRIDE = "leader_override"
    FALLBACK = "fallback"


class TaskState(str, Enum):
    """Execution state of an individual swarm task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class SwarmTask(BaseModel):
    """Individual unit of work assigned to a swarm agent."""

    task_id: str = Field(default_factory=lambda: f"stask_{uuid4().hex[:8]}")
    title: str
    description: str = ""
    required_role: AgentRole = AgentRole.SOFTWARE_ENGINEER
    dependencies: List[str] = Field(default_factory=list)
    state: TaskState = TaskState.PENDING
    assigned_agent_id: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SwarmAgentRecord(BaseModel):
    """Registered swarm agent metadata and load metrics."""

    agent_id: str
    name: str
    role: AgentRole
    capabilities: List[str] = Field(default_factory=list)
    is_busy: bool = False
    completed_tasks_count: int = 0
    confidence_rating: float = 1.0


class SwarmMessage(BaseModel):
    """Inter-agent message passed over the Swarm Message Bus."""

    message_id: str = Field(default_factory=lambda: f"smsg_{uuid4().hex[:8]}")
    sender_id: str
    receiver_id: str  # Specific agent_id or "broadcast"
    topic: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VoteRecord(BaseModel):
    """Vote submitted by a swarm agent."""

    vote_id: str = Field(default_factory=lambda: f"vote_{uuid4().hex[:8]}")
    agent_id: str
    option: str
    confidence: float = 1.0
    reasoning: str = ""


class ConsensusDecision(BaseModel):
    """Final consensus decision reached by voting engine."""

    decision_id: str = Field(default_factory=lambda: f"cdec_{uuid4().hex[:8]}")
    winning_option: str
    consensus_type: ConsensusType = ConsensusType.MAJORITY
    vote_breakdown: Dict[str, int] = Field(default_factory=dict)
    winning_confidence: float = 1.0


class BlackboardEntry(BaseModel):
    """Entry on the shared swarm blackboard."""

    key: str
    value: Any
    author_agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SwarmMissionGraph(BaseModel):
    """Directed Acyclic Graph (DAG) of swarm tasks."""

    graph_id: str = Field(default_factory=lambda: f"sgraph_{uuid4().hex[:8]}")
    goal: str
    tasks: List[SwarmTask] = Field(default_factory=list)


class SwarmResult(BaseModel):
    """Final aggregated output of a completed swarm execution."""

    swarm_id: str
    goal: str
    state: SwarmState = SwarmState.COMPLETED
    aggregated_output: Dict[str, Any] = Field(default_factory=dict)
    voice_summary: str = ""
    agents_involved: List[str] = Field(default_factory=list)
    execution_duration_seconds: float = 0.0


class SwarmMetrics(BaseModel):
    """Telemetry metrics for Swarm Intelligence Engine."""

    swarms_created: int = 0
    tasks_decomposed: int = 0
    tasks_executed: int = 0
    consensus_votes_held: int = 0
    conflicts_resolved: int = 0
    leader_elections_held: int = 0


class SwarmHealth(BaseModel):
    """Composite health status of Swarm Engine."""

    status: str = "healthy"
    active_swarms_count: int = 0
    total_registered_agents: int = 0
    subsystems_online: Dict[str, str] = Field(default_factory=dict)
