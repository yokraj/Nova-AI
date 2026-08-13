"""Workflow Recovery handling element missing timeouts and recovery strategies.
"""

from typing import Any, Dict
from app.ai.workflow_studio.models import WorkflowStep


class WorkflowRecovery:
    """Provides failure recovery strategies during step execution timeouts or missing UI controls."""

    def resolve_step_failure(self, step: WorkflowStep, error_msg: str) -> Dict[str, Any]:
        """Generates recovery action for failed step.

        Args:
            step: Failed WorkflowStep instance.
            error_msg: Error message string.

        Returns:
            Dictionary containing recovery_strategy and retry_recommended.
        """
        return {
            "step_id": step.step_id,
            "error": error_msg,
            "recovery_strategy": "visual_locator_fallback",
            "retry_recommended": True,
        }
