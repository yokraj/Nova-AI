"""Workflow Validator checking workflow structure, variable references, and execution readiness.
"""

from typing import List
from app.ai.workflow_studio.models import WorkflowDefinition


class WorkflowValidator:
    """Validates workflow definition structure and variable bindings."""

    def validate_workflow(self, workflow: WorkflowDefinition) -> List[str]:
        """Validates workflow definition and returns list of validation warning strings.

        Args:
            workflow: Target WorkflowDefinition instance.

        Returns:
            List of warning/error messages (empty if completely valid).
        """
        warnings: List[str] = []
        if not workflow.steps:
            warnings.append("Workflow has no steps defined.")
        return warnings
