"""Rollback Manager generates and executes state-reverting rollback sequences in LIFO order.
"""

import structlog
from typing import List, Dict, Any, Optional

from app.ai.automation.models import ActionStep, RollbackPlan, RollbackStep
from app.ai.automation.exceptions import RollbackError

logger = structlog.get_logger("rollback_manager")

class RollbackManager:
    """Maintains preceding execution states history and dispatches undo routines."""

    def __init__(self, provider: Optional[Any] = None) -> None:
        self.provider = provider
        self._history: List[RollbackStep] = []

    def record_action(self, step: ActionStep, pre_state: Dict[str, Any]) -> None:
        """Appends a corresponding undo step to the recovery stack based on the action state."""
        domain = step.domain

        if domain == "clipboard" and step.clipboard_action:
            action = step.clipboard_action
            if action.action_type in ("copy", "cut") and "text" in pre_state:
                self._history.append(
                    RollbackStep(
                        action_type="restore_clipboard",
                        target_data={"text": pre_state["text"]}
                    )
                )

        elif domain == "explorer" and step.explorer_action:
            action = step.explorer_action
            if action.action_type == "create_folder":
                self._history.append(
                    RollbackStep(
                        action_type="delete_file",
                        target_data={"path": action.path}
                    )
                )

        elif domain == "window" and step.window_action:
            action = step.window_action
            if action.action_type == "focus" and "title" in pre_state:
                self._history.append(
                    RollbackStep(
                        action_type="restore_focus",
                        target_data={"title": pre_state["title"]}
                    )
                )

    def get_plan(self) -> RollbackPlan:
        """Compiles the stack into an undo plan in LIFO order."""
        return RollbackPlan(steps=list(reversed(self._history)))

    async def execute_rollback(self, plan: RollbackPlan) -> bool:
        """Invokes sequential undo methods to reset environment parameters."""
        if not plan.steps:
            logger.info("Rollback plan is empty; no steps to execute.")
            return True

        logger.info("Executing state rollback plan", steps_count=len(plan.steps))
        success = True

        for step in plan.steps:
            try:
                logger.info("Executing rollback step", type=step.action_type, data=step.target_data)
                
                if step.action_type == "restore_clipboard":
                    if self.provider and hasattr(self.provider, "clipboard"):
                        self.provider.clipboard.copy(step.target_data.get("text", ""))
                
                elif step.action_type == "delete_file":
                    if self.provider and hasattr(self.provider, "explorer"):
                        self.provider.explorer.delete(step.target_data.get("path", ""))

                elif step.action_type == "restore_focus":
                    if self.provider and hasattr(self.provider, "window"):
                        self.provider.window.focus_window(step.target_data.get("title", ""))

            except Exception as err:
                logger.error("Failed to execute rollback step", action=step.action_type, error=str(err))
                success = False

        return success
