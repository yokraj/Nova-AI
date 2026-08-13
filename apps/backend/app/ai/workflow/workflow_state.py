"""Workflow State machine rules and transition validators.
"""

from app.ai.workflow.models import WorkflowState
from app.ai.workflow.exceptions import ExecutionError

class WorkflowStateMachine:
    """Validates state machine transitions for workflows and individual steps."""

    @staticmethod
    def transition(current: WorkflowState, new: WorkflowState) -> WorkflowState:
        """Asserts state transition safety rules."""
        valid = {
            WorkflowState.PENDING: [WorkflowState.RUNNING],
            WorkflowState.RUNNING: [WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.PAUSED],
            WorkflowState.PAUSED: [WorkflowState.RUNNING, WorkflowState.FAILED],
            WorkflowState.FAILED: [WorkflowState.PENDING, WorkflowState.RUNNING],
            WorkflowState.COMPLETED: []
        }

        if new in valid.get(current, []):
            return new

        # Graceful fallback or strict erroring
        if current == new:
            return current
        raise ExecutionError(f"Invalid workflow state transition: from {current} to {new}")
