"""Action Validator enforces runtime layout checks and coordinates bounds validation.
"""

import structlog
from typing import Optional, Any

from app.ai.automation.models import ActionStep
from app.ai.automation.exceptions import ActionValidationError
from app.ai.automation.safety_manager import SafetyManager
from app.ai.automation.permission_manager import PermissionManager

logger = structlog.get_logger("action_validator")

class ActionValidator:
    """Integrates safety audits and environment parameters validation."""

    def __init__(
        self,
        safety_mgr: Optional[SafetyManager] = None,
        permission_mgr: Optional[PermissionManager] = None,
        provider: Optional[Any] = None
    ) -> None:
        self.safety = safety_mgr or SafetyManager()
        self.permission = permission_mgr or PermissionManager()
        self.provider = provider

    def validate(self, step: ActionStep, permission_level: Optional[str] = None) -> None:
        """Performs validation before execution."""
        # Check permissions
        self.permission.check_permission(step, permission_level)

        # Check safety restrictions
        report = self.safety.validate_action(step)
        if not report.is_safe:
            raise ActionValidationError(f"Safety checks rejected the step: {'; '.join(report.violations)}")

        # Check environment/window existence
        if step.domain == "window" and step.window_action:
            action = step.window_action
            if action.action_type in ("focus", "close", "minimize", "maximize") and action.title:
                if self.provider and hasattr(self.provider, "window"):
                    matches = self.provider.window.search_by_title(action.title)
                    if not matches:
                        raise ActionValidationError(
                            f"Target window matching pattern '{action.title}' was not found on desktop"
                        )
                        
        elif step.domain == "process" and step.process_action:
            action = step.process_action
            if action.action_type == "terminate" and action.pid:
                if self.provider and hasattr(self.provider, "process"):
                    info = self.provider.process.monitor_process(action.pid)
                    if not info or info.get("status") == "terminated":
                        raise ActionValidationError(
                            f"Target process ID {action.pid} to terminate is already inactive"
                        )
