"""Abstract interfaces for components of the Workflow Orchestration Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.workflow.models import Workflow, WorkflowStep, WorkflowCheckpoint, ApprovalRequest, ApprovalResult

class IWorkflowPersistence(ABC):
    """Abstract store for serialized workflow states and checkpoints."""

    @abstractmethod
    def save_workflow(self, workflow: Workflow) -> None:
        """Saves current workflow state."""
        pass

    @abstractmethod
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Retrieves target workflow instance."""
        pass

    @abstractmethod
    def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> None:
        """Stores progress state checkpoint."""
        pass

    @abstractmethod
    def get_checkpoints(self, workflow_id: str) -> List[WorkflowCheckpoint]:
        """Lists stored checkpoints for a workflow."""
        pass

class IWorkflowScheduler(ABC):
    """Abstract scheduler ordering step runs based on dependencies."""

    @abstractmethod
    def enqueue(self, workflow: Workflow) -> None:
        """Enqueues workflow execution graph."""
        pass

    @abstractmethod
    def get_next_steps(self, workflow_id: str) -> List[WorkflowStep]:
        """Resolves current execution batch based on topological sorting dependencies."""
        pass

class IApprovalManager(ABC):
    """Abstract approval gating processor."""

    @abstractmethod
    def request_approval(self, request: ApprovalRequest) -> None:
        """Enqueues approval block on target step."""
        pass

    @abstractmethod
    def resolve_approval(self, approval_id: str, result: ApprovalResult) -> None:
        """Releases step blocking locks."""
        pass
