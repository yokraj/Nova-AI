"""Pydantic data models for the Autonomous Software Engineer Integration Engine.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AutonomousRequest(BaseModel):
    prompt: str = Field(..., description="The user instructions/goals.")
    environment: str = Field("production", description="Target environment.")
    variables: Dict[str, str] = Field(default_factory=dict, description="Environment configurations.")
    confirmations_enabled: bool = Field(True, description="Request user confirmations on destructive changes.")
    model_override: Optional[str] = Field(None, description="Local model override name.")

class WorkflowStep(BaseModel):
    id: str
    name: str
    target_engine: str = Field(..., description="Engine routing destination (e.g. Repository Analyzer, Code Generation Engine).")
    dependencies: List[str] = Field(default_factory=list, description="IDs of steps this step depends on.")
    status: str = Field("PLANNED", description="PLANNED, IN_PROGRESS, COMPLETED, FAILED, BYPASSED")

class Workflow(BaseModel):
    id: str
    steps: List[WorkflowStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WorkflowPlan(BaseModel):
    stages: List[str] = Field(default_factory=list)
    estimated_duration_sec: float = Field(0.0)

class TaskExecution(BaseModel):
    step_id: str
    success: bool = Field(True)
    duration_sec: float = Field(0.0)
    error_message: Optional[str] = Field(None)

class AgentCapability(BaseModel):
    engine_name: str
    is_available: bool = Field(True)
    supported_operations: List[str] = Field(default_factory=list)

class Decision(BaseModel):
    action_type: str = Field(..., description="The proposed action.")
    rationale: str = Field(..., description="Reasoning for the decision.")
    needs_user_confirmation: bool = Field(False)
    confirmed: bool = Field(True)

class ExecutionContext(BaseModel):
    workspace_root: str
    project_name: str
    git_branch: Optional[str] = Field(None)
    history_actions: List[str] = Field(default_factory=list)
    state_variables: Dict[str, Any] = Field(default_factory=dict)

class MemoryEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    category: str = Field(..., description="decision, code_fix, architecture, preference")
    description: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class Feedback(BaseModel):
    success: bool
    performance_score: float = Field(100.0)
    user_satisfaction: Optional[str] = Field(None)

class ValidationResult(BaseModel):
    gate_name: str
    passed: bool = Field(True)
    score: float = Field(100.0)
    errors: List[str] = Field(default_factory=list)

class QualityReport(BaseModel):
    overall_score: float = Field(100.0)
    results: List[ValidationResult] = Field(default_factory=list)

class RecoveryPlan(BaseModel):
    original_step_id: str
    action: str = Field(..., description="retry, rollback, skip, alternative")
    steps_to_execute: List[str] = Field(default_factory=list)

class ImprovementSuggestion(BaseModel):
    category: str
    issue_detected: str
    recommendation: str

class AutonomousResponse(BaseModel):
    status: str = Field(..., description="success, partial, failed")
    project_name: str
    workflow_executed: Workflow
    execution_timeline: List[TaskExecution] = Field(default_factory=list)
    quality_report: QualityReport
    report_markdown: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
