"""Automation Bridge connecting Service Engine workflows to AutomationRuntime."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("automation_bridge")


class AutomationBridge:
    """Delegates low-level browser/desktop actions from Service Workflows to AutomationRuntime."""

    def __init__(self, automation_runtime: Any = None) -> None:
        self.automation_runtime = automation_runtime

    async def execute_browser_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate browser action."""
        logger.info("AutomationBridge delegating browser action", action=action_name)
        if self.automation_runtime:
            from app.ai.automation.models import ActionType, AutomationRequest
            req = AutomationRequest(
                action_type=ActionType.BROWSER,
                action_name=action_name,
                parameters=parameters,
            )
            res = await self.automation_runtime.execute_automation(req)
            return {"status": "success", "success": res.success, "data": res.data}
        return {"status": "success", "action": action_name, "parameters": parameters}
