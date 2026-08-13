"""Pydantic V2 domain models for the Continuous Learning & Shared Experience Engine."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ExperienceType(str, Enum):
    """Classification of how the experience was acquired."""

    SUCCESS = "success"
    FAILURE = "failure"
    RECOVERY = "recovery"
    PARTIAL = "partial"


class ExperienceOutcome(str, Enum):
    """Final execution outcome of the mission or workflow that produced this experience."""

    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERED = "recovered"
    CANCELLED = "cancelled"


class LessonCategory(str, Enum):
    """Semantic category of a generated lesson."""

    SUCCESS = "success"
    FAILURE = "failure"
    OPTIMIZATION = "optimization"
    WARNING = "warning"


class RecommendationTarget(str, Enum):
    """Which engine or agent should receive this recommendation."""

    PLANNER = "planner"
    WORKFLOW = "workflow"
    MISSION = "mission"
    AGENT = "agent"
    SAFETY = "safety"


# ---------------------------------------------------------------------------
# Core Records
# ---------------------------------------------------------------------------

class Experience(BaseModel):
    """A persisted record of a completed or failed mission execution."""

    experience_id: str = Field(default_factory=lambda: f"exp_{uuid4().hex[:10]}")
    mission_id: str
    goal: str
    experience_type: ExperienceType
    outcome: ExperienceOutcome
    duration_seconds: float = 0.0
    agents_used: List[str] = Field(default_factory=list)
    workflow_id: Optional[str] = None
    lessons: List[str] = Field(default_factory=list)
    recovery_count: int = 0
    approval_count: int = 0
    user_satisfaction: float = 1.0  # 0.0 – 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Lesson(BaseModel):
    """A structured, human-readable lesson derived from an experience."""

    lesson_id: str = Field(default_factory=lambda: f"lsn_{uuid4().hex[:10]}")
    experience_id: str
    content: str
    category: LessonCategory
    confidence: float = 0.8  # 0.0 – 1.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Pattern(BaseModel):
    """A recurring behavioural pattern detected across multiple experiences."""

    pattern_id: str = Field(default_factory=lambda: f"ptn_{uuid4().hex[:10]}")
    name: str
    description: str
    occurrences: int = 0
    success_rate: float = 0.0  # 0.0 – 1.0
    agent_ids: List[str] = Field(default_factory=list)
    workflow_template: Optional[str] = None
    domain_keywords: List[str] = Field(default_factory=list)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)


class Strategy(BaseModel):
    """A reusable execution strategy derived from successful experience patterns."""

    strategy_id: str = Field(default_factory=lambda: f"str_{uuid4().hex[:10]}")
    name: str
    domain: str  # coding, debugging, ui_design, deployment, testing, planning, …
    version: int = 1
    description: str
    success_rate: float = 0.0
    usage_count: int = 0
    steps: List[str] = Field(default_factory=list)
    agent_preferences: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Recommendation(BaseModel):
    """A learning-derived recommendation issued to another engine or agent."""

    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid4().hex[:10]}")
    target: RecommendationTarget
    content: str
    strategy_id: Optional[str] = None
    pattern_id: Optional[str] = None
    confidence: float = 0.8
    goal_context: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentExperience(BaseModel):
    """Per-agent accumulated knowledge record."""

    agent_id: str
    total_missions: int = 0
    successful_missions: int = 0
    success_rate: float = 0.0
    preferred_strategies: List[str] = Field(default_factory=list)
    domain_expertise: Dict[str, float] = Field(default_factory=dict)  # domain -> score
    improvement_suggestions: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class LearningMetrics(BaseModel):
    """Snapshot of the learning engine's current key performance indicators."""

    total_experiences: int = 0
    success_rate: float = 0.0
    failure_rate: float = 0.0
    learned_strategies: int = 0
    pattern_matches: int = 0
    recommendations_generated: int = 0
    knowledge_reuse_pct: float = 0.0
    agent_learning_score: float = 0.0
    captured_at: datetime = Field(default_factory=datetime.utcnow)
