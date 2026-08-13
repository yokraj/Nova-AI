"""Workflow Debugger providing step-by-step execution, breakpoints, and state inspection.
"""

from typing import Any, Dict, List
from app.ai.workflow_studio.models import WorkflowDefinition


class WorkflowDebugger:
    """Provides step-by-step workflow debugging, breakpoint setting, and variable inspection."""

    def __init__(self) -> None:
        self._breakpoints: List[str] = []

    def set_breakpoint(self, step_id: str) -> None:
        """Sets breakpoint on step_id."""
        if step_id not in self._breakpoints:
            self._breakpoints.append(step_id)

    def inspect_step_state(self, workflow: WorkflowDefinition, current_step_index: int) -> Dict[str, Any]:
        """Inspects variable state at current step."""
        step = workflow.steps[current_step_index] if current_step_index < len(workflow.steps) else None
        return {
            "step_id": step.step_id if step else None,
            "description": step.description if step else None,
            "has_breakpoint": (step.step_id in self._breakpoints) if step else False,
        }
