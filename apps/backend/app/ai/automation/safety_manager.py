"""Safety Manager validates visual coordinates and shell scripts commands before execution.
"""

import structlog
from typing import Optional

from app.ai.automation.exceptions import SafetyViolationError
from app.ai.automation.models import ActionStep, SafetyReport
from app.ai.automation.configuration import SafetyConfiguration

logger = structlog.get_logger("safety_manager")

class SafetyManager:
    """Enforces execution guards, screen blocklist coordinates, and shell command blocks."""

    def __init__(self, config: Optional[SafetyConfiguration] = None) -> None:
        self.config = config or SafetyConfiguration()

    def validate_action(self, step: ActionStep) -> SafetyReport:
        """Audits target step coordinates, commands, and arguments to ensure compliance."""
        report = SafetyReport(is_safe=True)

        # Verify mouse coordinates boundary constraints
        if step.domain == "mouse" and step.mouse_action:
            action = step.mouse_action
            if action.x is not None and action.y is not None:
                if not (0.0 <= action.x <= 1.0) or not (0.0 <= action.y <= 1.0):
                    report.is_safe = False
                    report.violations.append(
                        f"Target coordinates ({action.x}, {action.y}) are outside normalized scale [0.0 - 1.0]"
                    )
                
                # Check safety regions constraints (mapped to simulated standard workspace pixels)
                pixel_x = int(action.x * 1920)
                pixel_y = int(action.y * 1080)
                for region in self.config.safety_regions:
                    x1, y1, x2, y2 = region
                    if x1 <= pixel_x <= x2 and y1 <= pixel_y <= y2:
                        report.is_safe = False
                        report.violations.append(
                            f"Target coordinates map to forbidden safety region: {region} at ({pixel_x}, {pixel_y})"
                        )

        # Check shell script commands for blocked command keywords
        elif step.domain == "terminal" and step.terminal_action:
            action = step.terminal_action
            if action.command:
                cmd_lower = action.command.lower()
                for banned in self.config.command_blocklist:
                    if banned in cmd_lower:
                        report.is_safe = False
                        report.violations.append(
                            f"Shell script command contains prohibited keyword: '{banned}'"
                        )

        # Check file explorer operations
        elif step.domain == "explorer" and step.explorer_action:
            action = step.explorer_action
            if action.action_type == "delete":
                path_lower = action.path.replace("/", "\\").lower().strip()
                if path_lower in ("c:", "c:\\", "c:\\windows", "c:\\windows\\system32"):
                    report.is_safe = False
                    report.violations.append(
                        f"Deletions of critical system path '{action.path}' are prohibited"
                    )

        if not report.is_safe:
            logger.warning(
                "Safety audit failed for action step",
                step_id=step.step_id,
                domain=step.domain,
                violations=report.violations
            )
            report.interventions_count = len(report.violations)

        return report
