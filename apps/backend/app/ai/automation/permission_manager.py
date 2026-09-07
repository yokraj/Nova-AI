"""Permission Manager intercepting dangerous automation actions and delegating to Safety Engine."""

from typing import Any, Dict, List
import structlog

from app.ai.automation.configuration import AutomationConfiguration
from app.ai.automation.exceptions import AutomationSafetyError

logger = structlog.get_logger("permission_manager")


class AutomationPermissionManager:
    """Evaluates security permissions and intercepts dangerous automation actions (payments, file deletion, purchases, system settings, software installation)."""

    DANGEROUS_ACTIONS: List[str] = [
        "payment",
        "make_payment",
        "delete_file",
        "delete_directory",
        "purchase",
        "buy_now",
        "change_system_setting",
        "install_software",
        "format_drive",
    ]

    def __init__(self, config: Optional[AutomationConfiguration] = None) -> None:
        self.config = config or AutomationConfiguration()

    async def verify_permission(self, action_name: str, parameters: Dict[str, Any]) -> bool:
        """Verify whether action is safe to execute or requires human approval."""
        action_clean = action_name.lower().strip()

        is_dangerous = any(d in action_clean for d in self.DANGEROUS_ACTIONS)
        if is_dangerous:
            logger.warning("Dangerous automation action intercepted", action=action_name)
            # Delegate to Safety Engine / Human Approval
            try:
                from app.ai.gateway import IAIGateway
                from app.core.dependency_container import resolve
                gateway = resolve(IAIGateway)
                approved = await gateway.request_approval(
                    action=f"Automation Action: {action_name}",
                    description=f"Automated action requires human confirmation: {parameters}",
                )
                if not approved:
                    raise AutomationSafetyError(f"Dangerous action '{action_name}' rejected by user.")
                return True
            except Exception as e:
                if isinstance(e, AutomationSafetyError):
                    raise
                logger.info("Safety Engine gateway fallback approved for dry run testing", error=str(e))
                if self.config.safety_dry_run:
                    return True
                raise AutomationSafetyError(f"Dangerous action '{action_name}' requires human approval: {e}")

        return True


PermissionManager = AutomationPermissionManager

