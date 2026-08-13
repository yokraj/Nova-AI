"""LocalAutomationEngine coordinates the full sequence of validation, safety, and execution.
"""

import time
import structlog
from typing import Optional, Any

from app.ai.automation.configuration import AutomationConfiguration
from app.ai.automation.models import (
    AutomationRequest,
    AutomationResponse,
    AutomationMetrics,
    SafetyReport,
    ExecutionResult
)
from app.ai.automation.providers.mock_provider import MockAutomationProvider
from app.ai.automation.providers.pyautogui_provider import PyAutoGUIProvider
from app.ai.automation.permission_manager import PermissionManager
from app.ai.automation.safety_manager import SafetyManager
from app.ai.automation.rollback_manager import RollbackManager
from app.ai.automation.action_validator import ActionValidator
from app.ai.automation.action_executor import ActionExecutor
from app.ai.automation.context_builder import ContextBuilder
from app.ai.automation.memory import AutomationMemory
from app.ai.automation.metrics import AutomationMetricsTracker
from app.ai.automation.cache import AutomationCache
from app.ai.automation.mouse_controller import MouseController
from app.ai.automation.keyboard_controller import KeyboardController
from app.ai.automation.browser_controller import BrowserController
from app.ai.automation.execution_context import ExecutionContext

logger = structlog.get_logger("automation_engine")

class LocalAutomationEngine:
    """Coordinating central orchestrator for safety checks, dispatches, and recoveries."""

    def __init__(
        self,
        config: Optional[AutomationConfiguration] = None,
        gateway: Optional[Any] = None,
        memory_engine: Optional[Any] = None
    ) -> None:
        self.config = config or AutomationConfiguration()
        self.gateway = gateway

        # Resolve provider
        if self.config.provider == "pyautogui":
            self.provider = PyAutoGUIProvider(dry_run=self.config.safety.dry_run)
        else:
            self.provider = MockAutomationProvider()

        # Managers
        self.permission = PermissionManager(self.config.permission_level)
        self.safety = SafetyManager(self.config.safety)
        self.rollback = RollbackManager(self.provider)
        self.validator = ActionValidator(self.safety, self.permission, self.provider)

        # Controllers
        self.mouse = MouseController(self.provider)
        self.keyboard = KeyboardController(self.provider)
        self.browser = BrowserController(self.provider)

        # Action Executor dispatches steps to controllers
        self.executor = ActionExecutor(
            mouse_ctrl=self.mouse,
            keyboard_ctrl=self.keyboard,
            clipboard_mgr=self.provider.clipboard,
            window_mgr=self.provider.window,
            browser_ctrl=self.browser,
            explorer_ctrl=self.provider.explorer,
            terminal_ctrl=self.provider.terminal,
            process_mgr=self.provider.process
        )

        self.context_builder = ContextBuilder(self.provider)
        self.memory = AutomationMemory(memory_engine)
        self.metrics_tracker = AutomationMetricsTracker()
        self.cache = AutomationCache()

    async def execute(self, request: AutomationRequest) -> AutomationResponse:
        """Executes action steps sequence, validating parameters and initiating rollback on failures."""
        self.metrics_tracker.reset()
        self.metrics_tracker.start_stage("total")

        # Verify cached responses
        cached = self.cache.get(request.request_id)
        if cached:
            return cached

        exec_ctx = ExecutionContext()
        results: list[ExecutionResult] = []
        overall_status = "success"
        rollback_triggered = False
        error_msg = None
        overall_safety = SafetyReport(is_safe=True)

        sys_ctx = self.context_builder.build_context()
        logger.info("Initializing desktop automation sequence execution", request_id=request.request_id, active_context=sys_ctx)

        # Dry run parameters validation
        is_dry_run = request.dry_run if request.dry_run is not None else self.config.safety.dry_run

        for step in request.sequence.steps:
            # 1. Action permissions and safety validation
            self.metrics_tracker.start_stage("validate")
            try:
                perm_level = request.permission_level or self.config.permission_level
                self.validator.validate(step, perm_level)
            except Exception as err:
                self.metrics_tracker.increment("validation_failures")
                self.metrics_tracker.end_stage("validate")
                overall_status = "blocked_by_safety"
                overall_safety.is_safe = False
                overall_safety.violations.append(str(err))
                error_msg = f"Safety/Validation checks blocked step execution: {str(err)}"
                break
            self.metrics_tracker.end_stage("validate")

            # 2. Record pre-execution state for rollbacks
            pre_state = {}
            if step.domain == "clipboard":
                pre_state["text"] = self.provider.clipboard.paste()
            elif step.domain == "window":
                active = self.provider.window.active_window()
                if active:
                    pre_state["title"] = active.get("title", "")

            self.rollback.record_action(step, pre_state)

            # 3. Step execution
            self.metrics_tracker.start_stage("execute")
            if is_dry_run:
                # Capture simulated execution parameters
                res = ExecutionResult(
                    step_id=step.step_id,
                    status="success",
                    stdout=f"Simulated execution for domain: {step.domain}"
                )
            else:
                res = await self.executor.execute_step(step, exec_ctx)
                
            self.metrics_tracker.increment("actions_executed")
            self.metrics_tracker.end_stage("execute")

            results.append(res)

            if res.status == "failed":
                overall_status = "failed"
                error_msg = res.error_message

                # Trigger rollback recover sequence
                self.metrics_tracker.start_stage("rollback")
                rollback_plan = self.rollback.get_plan()
                await self.rollback.execute_rollback(rollback_plan)
                self.metrics_tracker.increment("rollback_count")
                rollback_triggered = True
                self.metrics_tracker.end_stage("rollback")
                break

        self.metrics_tracker.end_stage("total")
        timings = self.metrics_tracker.get_metrics()

        # RAG memory store
        cmd_summary = f"Playback sequence {request.sequence.sequence_id} containing {len(request.sequence.steps)} actions"
        results_summary = f"Ran {len(results)} steps, final state: {overall_status}"
        perf_summary = f"Execution duration: {timings.get('total', 0.0):.2f}ms"
        await self.memory.store_execution(cmd_summary, results_summary, perf_summary)
        self.metrics_tracker.increment("memory_writes")

        # Compile final telemetry metrics
        metrics = AutomationMetrics(
            total_duration_ms=timings.get("total", 0.0),
            steps_executed=self.metrics_tracker.counts["actions_executed"],
            steps_failed=self.metrics_tracker.counts.get("steps_failed", 0),
            safety_interventions=self.metrics_tracker.counts.get("safety_interventions", 0),
            rollback_triggered=rollback_triggered,
            rollback_duration_ms=timings.get("rollback", 0.0)
        )

        response = AutomationResponse(
            request_id=request.request_id,
            status=overall_status,
            results=results,
            safety_report=overall_safety,
            metrics=metrics,
            rollback_plan=self.rollback.get_plan(),
            error_message=error_msg
        )

        self.cache.set(request.request_id, response)
        return response
