"""State Persistence layer saving workflows and checkpoints histories.
"""

from typing import Dict, List, Optional
from app.ai.workflow.models import Workflow, WorkflowCheckpoint
from app.ai.workflow.interfaces import IWorkflowPersistence

class StatePersistence(IWorkflowPersistence):
    """Saves serialized workflow nodes and snapshots locally in memory/disk."""

    def __init__(self) -> None:
        self._workflows: Dict[str, Workflow] = {}
        self._checkpoints: Dict[str, List[WorkflowCheckpoint]] = {}

    def save_workflow(self, workflow: Workflow) -> None:
        """Saves target workflow current state."""
        self._workflows[workflow.workflow_id] = workflow.model_copy()

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Retrieves targeted active workflow."""
        return self._workflows.get(workflow_id)

    def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> None:
        """Appends snapshot record to checkpoint log history."""
        w_id = checkpoint.workflow_id
        if w_id not in self._checkpoints:
            self._checkpoints[w_id] = []
        self._checkpoints[w_id].append(checkpoint)

    def get_checkpoints(self, workflow_id: str) -> List[WorkflowCheckpoint]:
        """Returns sorted list of checkpoint snapshots."""
        return self._checkpoints.get(workflow_id, [])
