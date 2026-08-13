"""Workflow Editor allowing step editing, variable binding, conditions, and loops.
"""

from typing import Any, Dict
from app.ai.workflow_studio.models import WorkflowDefinition, WorkflowStep


class WorkflowEditor:
    """Provides editing API for modifying workflow steps, variables, and conditions."""

    def add_step(self, workflow: WorkflowDefinition, step: WorkflowStep) -> WorkflowDefinition:
        """Appends step to workflow."""
        workflow.steps.append(step)
        return workflow

    def remove_step(self, workflow: WorkflowDefinition, step_id: str) -> WorkflowDefinition:
        """Removes step by step_id from workflow."""
        workflow.steps = [s for s in workflow.steps if s.step_id != step_id]
        return workflow
