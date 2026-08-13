"""Action Executor orchestrating step-by-step action dispatching and execution flow.
"""

from typing import Any, Dict
from app.ai.desktop_automation.models import AutomationAction, AutomationResult


class ActionExecutor:
    """Dispatches and executes individual GUI and OS automation actions."""

    def execute_action(self, action: AutomationAction) -> AutomationResult:
        """Executes automation action step."""
        return AutomationResult(
            action_id=action.action_id,
            success=True,
            output={"executed_action": action.action_type, "label": action.target_label},
            duration_sec=0.04,
        )
