"""Pydantic data models, enums, and schemas for Autonomous Self-Improvement & Adaptive Intelligence Engine.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class OptimizationScope(str, Enum):
    """Enumerate subsystem optimization scopes."""

    WORKFLOW = "workflow"
    PLANNER = "planner"
    AGENT = "agent"
    AUTOMATION = "automation"
    CONVERSATION = "conversation"
    RESEARCH = "research"
    COPILOT = "copilot"
    VISION = "vision"
    RUNTIME = "runtime"


class EvaluationCycle(str, Enum):
    """Enumerate self-evaluation benchmark cycles."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class RegressionStatus(str, Enum):
    """Enumerate regression detection statuses."""

    NORMAL = "normal"
    WARNING = "warning"
    REGRESSION_DETECTED = "regression_detected"


class OptimizationStatus(str, Enum):
    """Enumerate optimization recommendation lifecycle states."""

    PROPOSED = "proposed"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"


class PerformanceMetricsSnapshot(BaseModel):
    """Snapshot model for subsystem performance telemetry."""

    subsystem_name: str = Field(...)
    latency_ms: float = Field(120.0)
    success_rate: float = Field(0.98)
    throughput_qps: float = Field(15.0)
    memory_usage_mb: float = Field(256.0)


class AgentScorecard(BaseModel):
    """Evaluation scorecard for an individual agent in the workforce."""

    agent_name: str = Field(...)
    role: str = Field("software_engineer")
    latency_ms: float = Field(95.0)
    accuracy_score: float = Field(0.96)
    success_rate: float = Field(0.98)
    reliability_score: float = Field(0.99)
    recovery_rate: float = Field(0.95)


class ExperiencePackage(BaseModel):
    """Distilled experience package containing reusable skills and templates."""

    package_id: str = Field(default_factory=lambda: f"exp_{uuid.uuid4().hex[:8]}")
    name: str = Field(...)
    workflow_steps: List[str] = Field(default_factory=list)
    reusable_skill_id: Optional[str] = Field(None)
    automation_template_id: Optional[str] = Field(None)
    mission_template_id: Optional[str] = Field(None)
    created_at: float = Field(default_factory=time.time)


class WorkflowOptimizationRecommendation(BaseModel):
    """Recommendation model for workflow step optimizations."""

    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:8]}")
    original_workflow_id: str = Field(...)
    optimized_steps: List[str] = Field(default_factory=list)
    latency_reduction_pct: float = Field(25.0)
    confidence: float = Field(0.92)
    status: OptimizationStatus = Field(OptimizationStatus.PROPOSED)


class BenchmarkReport(BaseModel):
    """Historical benchmark evaluation report."""

    report_id: str = Field(default_factory=lambda: f"bench_{uuid.uuid4().hex[:8]}")
    cycle: EvaluationCycle = Field(EvaluationCycle.DAILY)
    agent_scorecards: List[AgentScorecard] = Field(default_factory=list)
    overall_score: float = Field(0.96)
    timestamp: float = Field(default_factory=time.time)


class QualityDiagnosticReport(BaseModel):
    """Quality diagnostic report detecting regressions and failure patterns."""

    report_id: str = Field(default_factory=lambda: f"qual_{uuid.uuid4().hex[:8]}")
    status: RegressionStatus = Field(RegressionStatus.NORMAL)
    regressions_found: List[str] = Field(default_factory=list)
    failure_patterns: List[str] = Field(default_factory=list)
    agent_conflicts: List[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class SelfImprovementHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    total_optimizations_applied: int = Field(0)
    active_evaluations_count: int = Field(0)
    timestamp: float = Field(default_factory=time.time)


class SelfImprovementMetrics(BaseModel):
    """Telemetry collector metrics model."""

    total_evaluations: int = Field(0)
    optimizations_applied: int = Field(0)
    experiences_distilled: int = Field(0)
    regressions_prevented: int = Field(0)
    timestamp: float = Field(default_factory=time.time)
