"""Dependency Manager identifying unblocked step batches based on completions logs.
"""

from typing import Dict, List, Set
from app.ai.workflow.models import WorkflowStep, WorkflowState

class DependencyManager:
    """Manages active dependency constraints across steps."""

    def is_blocked(self, step: WorkflowStep, completed_step_ids: Set[str]) -> bool:
        """Returns True if any of the step's dependencies are not yet completed."""
        return not set(step.dependencies).issubset(completed_step_ids)

    def get_unblocked_steps(self, steps: Dict[str, WorkflowStep], completed_step_ids: Set[str]) -> List[WorkflowStep]:
        """Resolves step subset where dependencies are fully satisfied and state is pending."""
        unblocked = []
        for step in steps.values():
            if step.state == WorkflowState.PENDING and not self.is_blocked(step, completed_step_ids):
                unblocked.append(step)
        return unblocked
