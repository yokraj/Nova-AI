"""Workflow represents the active pipeline structure.
"""

from typing import List
from app.agents.software_engineer.autonomous.models import Workflow, WorkflowStep

class WorkflowHelper:
    """Provides helper routines to inspect and update workflow step progress."""

    @staticmethod
    def get_incomplete_steps(workflow: Workflow) -> List[WorkflowStep]:
        """Returns lists of steps that have not been completed successfully."""
        return [step for step in workflow.steps if step.status not in ("COMPLETED", "BYPASSED")]

    @staticmethod
    def mark_step_status(workflow: Workflow, step_id: str, status: str) -> None:
        """Finds a step by id and updates its execution status."""
        for step in workflow.steps:
            if step.id == step_id:
                step.status = status
                break
