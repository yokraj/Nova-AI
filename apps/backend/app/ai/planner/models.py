"""Pydantic V2 domain models for the Intelligent Planner & Task Decomposition Engine.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class Goal(BaseModel):
    """Represents a natural language goal submitted by a user."""
    goal_id: str
    description: str
    context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CapabilityRequirement(BaseModel):
    """Specifies capabilities an agent must possess to run a task."""
    capability_name: str
    minimum_score: float = 0.5
    importance: str = "required"  # required, preferred

class AgentAssignment(BaseModel):
    """Represents agent selection details assigned to a task."""
    agent_id: str
    agent_name: str
    capability_score: float
    confidence: float
    fallback_agent_ids: List[str] = Field(default_factory=list)

class CostEstimate(BaseModel):
    """Estimates of computing cost metrics for running a task."""
    cpu_cores: float = 0.5
    memory_mb: int = 512
    token_limit: int = 4096
    monetary_cents: float = 0.0

class TimeEstimate(BaseModel):
    """Duration limits for task executions."""
    estimated_seconds: float
    maximum_timeout_seconds: float
    confidence_score: float

class RiskAssessment(BaseModel):
    """Identifies architectural or operational risks associated with a task."""
    risk_level: str = "low"  # low, medium, high
    description: str = ""
    mitigation_strategy: str = ""

class Task(BaseModel):
    """A specific execution node details model."""
    task_id: str
    parent_id: Optional[str] = None
    title: str
    description: str
    domain: str = "generic"
    status: str = "pending"  # pending, ready, completed, failed
    priority: str = "Medium"  # Critical, High, Medium, Low
    required_capabilities: List[CapabilityRequirement] = Field(default_factory=list)
    assignment: Optional[AgentAssignment] = None
    time_estimate: Optional[TimeEstimate] = None
    cost_estimate: Optional[CostEstimate] = None
    risk: Optional[RiskAssessment] = None
    dependencies: List[str] = Field(default_factory=list)

class TaskNode(BaseModel):
    """Node wrapping hierarchical representations inside a TaskTree."""
    task: Task
    children: List["TaskNode"] = Field(default_factory=list)

class TaskTree(BaseModel):
    """Represents task hierarchy decompositions."""
    root_node: TaskNode
    total_nodes: int = 1

class Dependency(BaseModel):
    """Represents a directional edge in a dependency graph."""
    dependency_id: str
    source_task_id: str
    target_task_id: str

class DependencyGraph(BaseModel):
    """The complete DAG structure mapping sequential execution constraints."""
    nodes: Dict[str, Task] = Field(default_factory=dict)
    edges: List[Dependency] = Field(default_factory=list)
    critical_path: List[str] = Field(default_factory=list)

class ExecutionBatch(BaseModel):
    """A group of independent tasks that can be run concurrently."""
    batch_id: str
    task_ids: List[str] = Field(default_factory=list)
    estimated_duration_seconds: float = 0.0

class RecoveryPlan(BaseModel):
    """Alternative execution paths on failure conditions."""
    task_id: str
    alternate_agent_ids: List[str] = Field(default_factory=list)
    degraded_execution_params: Dict[str, Any] = Field(default_factory=dict)
    allow_retry: bool = True
    max_retries: int = 3

class ExecutionPlan(BaseModel):
    """Complete schedule detailing execution batches, recovery plans, and total limits."""
    plan_id: str
    batches: List[ExecutionBatch] = Field(default_factory=list)
    recovery_plans: Dict[str, RecoveryPlan] = Field(default_factory=dict)
    total_estimated_seconds: float = 0.0

class PlanningMetrics(BaseModel):
    """Telemetry timings computed during plan compilations."""
    planning_latency_ms: float = 0.0
    decomposition_depth: int = 0
    task_count: int = 0
    dag_size: int = 0
    optimization_ratio: float = 1.0

class PlanningRequest(BaseModel):
    """Request payload initiating planning pipelines."""
    request_id: str
    goal: str
    context: Dict[str, Any] = Field(default_factory=dict)
    force_replanning: bool = False
    dry_run: bool = True

class PlanningResponse(BaseModel):
    """Response returned upon compiling plan structures."""
    session_id: str
    status: str  # success, failed
    task_tree: TaskTree
    dependency_graph: DependencyGraph
    execution_plan: ExecutionPlan
    metrics: PlanningMetrics
    error_message: Optional[str] = None

class PlanningSession(BaseModel):
    """Active planner session variables."""
    session_id: str
    goal: Goal
    task_tree: Optional[TaskTree] = None
    dependency_graph: Optional[DependencyGraph] = None
    execution_plan: Optional[ExecutionPlan] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class OptimizationResult(BaseModel):
    """Stores optimizations results metrics."""
    original_batches_count: int
    optimized_batches_count: int
    parallelism_ratio: float

class PlannerStatistics(BaseModel):
    """Global system planners usage indicators."""
    total_sessions_count: int = 0
    successful_sessions_count: int = 0
    average_planning_latency_ms: float = 0.0
