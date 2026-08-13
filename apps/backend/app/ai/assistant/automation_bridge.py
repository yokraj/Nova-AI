"""Automation Bridge connecting Assistant Engine to AutomationRuntime."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("assistant_automation_bridge")


class AutomationBridge:
    """Delegates browser/desktop automation tasks from Assistant Engine to AutomationRuntime."""

    def __init__(self, automation_runtime: Any = None) -> None:
        self.automation_runtime = automation_runtime

    async def execute_desktop_launch(self, app_name: str) -> Dict[str, Any]:
        """Launch desktop app."""
        logger.info("AutomationBridge launching app", app=app_name)
        if self.automation_runtime:
            from app.ai.automation.models import ActionType, AutomationRequest
            req = AutomationRequest(
                action_type=ActionType.DESKTOP,
                action_name="launch",
                parameters={"app": app_name},
            )
            res = await self.automation_runtime.execute_automation(req)
            return {"status": "success", "data": res.data}
        return {"status": "success", "app": app_name}
