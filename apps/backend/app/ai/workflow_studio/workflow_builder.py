"""Workflow Builder assembling WorkflowDefinition objects from extracted steps and variables.
"""

from typing import List, Optional
from app.ai.workflow_studio.models import (
    WorkflowDefinition,
    WorkflowStep,
    WorkflowTrigger,
    WorkflowVariable,
)


class WorkflowBuilder:
    """Assembles structured WorkflowDefinition objects from steps, variables, and triggers."""

    def build_workflow(
        self,
        name: str,
        steps: List[WorkflowStep],
        variables: Optional[List[WorkflowVariable]] = None,
        triggers: Optional[List[WorkflowTrigger]] = None,
    ) -> WorkflowDefinition:
        """Assembles and returns WorkflowDefinition instance.

        Args:
            name: Workflow name string.
            steps: List of WorkflowStep objects.
            variables: Optional list of WorkflowVariable objects.
            triggers: Optional list of WorkflowTrigger objects.

        Returns:
            WorkflowDefinition model instance.
        """
        return WorkflowDefinition(
            name=name,
            steps=steps,
            variables=variables or [],
            triggers=triggers or [],
        )
