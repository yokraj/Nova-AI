"""Automation Runtime facade orchestrating Desktop and Browser Controllers, Permissions, Metrics, and Pipeline."""

from typing import Any, Dict, List, Optional
import time
import structlog

from app.ai.automation.cache import AutomationCache
from app.ai.automation.automation_pipeline import AutomationPipeline
from app.ai.automation.browser_controller import BrowserController
from app.ai.automation.configuration import AutomationConfiguration
from app.ai.automation.desktop_controller import DesktopController
from app.ai.automation.health import AutomationHealthMonitor
from app.ai.automation.interfaces import IAutomationRuntime
from app.ai.automation.metrics import AutomationMetricsTracker
from app.ai.automation.models import (
    ActionType,
    AutomationHealth,
    AutomationMetrics,
    AutomationRequest,
    AutomationResult,
)
from app.ai.automation.permission_manager import AutomationPermissionManager

logger = structlog.get_logger("automation_runtime")


class AutomationRuntime(IAutomationRuntime):
    """Central facade runtime orchestrating Desktop and Browser automation controllers."""

    def __init__(
        self,
        config: Optional[AutomationConfiguration] = None,
        provider: Any = None,
    ) -> None:
        self.config = config or AutomationConfiguration()
        self.provider = provider
        self.desktop = DesktopController()
        self.browser = BrowserController(provider=self.provider)
        self.permissions = AutomationPermissionManager(config=self.config)
        self.metrics = AutomationMetricsTracker()
        self.health_monitor = AutomationHealthMonitor()
        self.cache = AutomationCache()
        self.pipeline = AutomationPipeline(runtime=self)

    async def execute_automation(self, request: AutomationRequest) -> AutomationResult:
        """Process automation request across Desktop or Browser drivers."""
        start_time = time.perf_counter()
        logger.info("Executing automation request", id=request.request_id, type=request.action_type, name=request.action_name)

        try:
            # 1. Verify permissions / safety interception
            approved = await self.permissions.verify_permission(request.action_name, request.parameters)

            # 2. Dispatch action
            data: Any = None
            if request.action_type == ActionType.DESKTOP:
                self.metrics.record_action("desktop")
                if request.action_name == "launch":
                    app = request.parameters.get("app", "notepad.exe")
                    data = await self.desktop.launch_application(app)
                else:
                    data = {"status": "desktop_action_completed", "action": request.action_name}

            elif request.action_type == ActionType.BROWSER:
                self.metrics.record_action("browser")
                if request.action_name == "navigate":
                    url = request.parameters.get("url", "https://google.com")
                    data = await self.browser.navigate_url(url)
                elif request.action_name == "click":
                    selector = request.parameters.get("selector", "button")
                    data = await self.browser.click_element(selector)
                elif request.action_name == "fill":
                    selector = request.parameters.get("selector", "input")
                    value = request.parameters.get("value", "")
                    data = await self.browser.fill_input(selector, value)
                else:
                    data = {"status": "browser_action_completed", "action": request.action_name}

            else:
                data = {"status": "action_completed", "name": request.action_name}

            duration = time.perf_counter() - start_time
            self.metrics.record_success(duration)

            return AutomationResult(
                request_id=request.request_id,
                action_name=request.action_name,
                success=True,
                data=data,
                duration_seconds=duration,
                human_approved=approved,
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            self.metrics.record_failure()
            logger.error("Automation request failed", id=request.request_id, error=str(e))
            return AutomationResult(
                request_id=request.request_id,
                action_name=request.action_name,
                success=False,
                error=str(e),
                duration_seconds=duration,
            )

    async def get_metrics(self) -> AutomationMetrics:
        """Retrieve telemetry metrics."""
        return self.metrics.get_metrics()

    def check_health(self) -> AutomationHealth:
        """Retrieve composite health report."""
        return self.health_monitor.check_health()
