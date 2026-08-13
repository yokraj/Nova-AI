"""Interfaces for the Autonomous Software Engineer Integration Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.agents.software_engineer.autonomous.models import (
    AutonomousRequest,
    AutonomousResponse,
    Workflow,
    WorkflowStep,
    WorkflowPlan,
    TaskExecution,
    AgentCapability,
    Decision,
    ExecutionContext,
    MemoryEntry,
    Feedback,
    QualityReport,
    ValidationResult,
    RecoveryPlan,
    ImprovementSuggestion,
)

class IWorkflowBuilder(ABC):
    """Abstract interface for dynamic workflow building."""

    @abstractmethod
    def build_workflow(self, request: AutonomousRequest, context: ExecutionContext) -> Workflow:
        """Dynamically generates a workflow plan matching the request characteristics."""
        pass

class IWorkflowExecutor(ABC):
    """Abstract interface for executing workflow steps."""

    @abstractmethod
    async def execute_workflow(self, workflow: Workflow, context: ExecutionContext) -> List[TaskExecution]:
        """Runs the generated steps sequence, checking quality gates and triggers."""
        pass

class ITaskOrchestrator(ABC):
    """Abstract interface for task ordering and retries."""

    @abstractmethod
    def order_tasks(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Orders task steps topologically, setting dependencies."""
        pass

class IAgentRouter(ABC):
    """Abstract interface for routing requests to specialized sub-engines."""

    @abstractmethod
    def route_request(self, task_description: str) -> str:
        """Returns the name of the target capability engine to execute this task."""
        pass

class IDecisionEngine(ABC):
    """Abstract interface for the system reasoning layer."""

    @abstractmethod
    def validate_action(self, decision: Decision) -> bool:
        """Determines if the action is safe or requires user confirmation."""
        pass

class IMemoryManager(ABC):
    """Abstract interface for sync and loading execution memories."""

    @abstractmethod
    def commit_memory(self, entry: MemoryEntry) -> None:
        """Saves decisions and completed tasks context to history."""
        pass

class IValidator(ABC):
    """Abstract interface for Self-Validation and Quality Gates."""

    @abstractmethod
    def validate_gates(self, context: ExecutionContext) -> QualityReport:
        """Runs validation checks across all 5 Quality Gates."""
        pass

class IRecoveryManager(ABC):
    """Abstract interface for error rollback strategies."""

    @abstractmethod
    def build_recovery_plan(self, failed_task: TaskExecution) -> RecoveryPlan:
        """Generates rollback instructions or alternative tasks list."""
        pass

class IImprovementEngine(ABC):
    """Abstract interface for self-improvement and optimization recommendations."""

    @abstractmethod
    def analyze_feedback(self, feedback: Feedback) -> List[ImprovementSuggestion]:
        """Analyzes outcome metrics to output learning notes."""
        pass

class IAutonomousEngine(ABC):
    """Abstract interface for the orchestrating Autonomous Engine."""

    @abstractmethod
    async def execute_autonomous_workflow(self, request: AutonomousRequest) -> AutonomousResponse:
        """Executes the full 15-stage workflow pipeline."""
        pass
