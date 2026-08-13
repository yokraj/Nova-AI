"""Central AI Operating System Kernel Engine orchestrating all Nova AI capabilities through one unified runtime.
"""

import time
from typing import Any, Dict, Optional, Union
from app.ai.kernel.capability_resolver import CapabilityResolver
from app.ai.kernel.configuration import KernelConfiguration
from app.ai.kernel.context_engine import ContextEngine
from app.ai.kernel.copilot_integration import CopilotIntegration
from app.ai.kernel.dynamic_planner import DynamicPlanner
from app.ai.kernel.event_bus import EventBus
from app.ai.kernel.exceptions import KernelStateError, SecurityApprovalRequiredError
from app.ai.kernel.health import KernelHealthMonitor
from app.ai.kernel.intent_engine import IntentEngine
from app.ai.kernel.interfaces import IKernelEngine
from app.ai.kernel.kernel_manager import KernelManager
from app.ai.kernel.kernel_security import KernelSecurityGuard
from app.ai.kernel.metrics import KernelMetricsTracker
from app.ai.kernel.models import (
    CapabilityMatch,
    ExecutionContext,
    ExecutionPlan,
    IntentRequest,
    IntentResponse,
    KernelHealth,
    KernelMetrics,
    KernelState,
    OperatingMode,
    PriorityLevel,
    SystemSnapshot,
    VerificationResult,
)
from app.ai.kernel.os_memory import OSMemory
from app.ai.kernel.resource_manager import SystemResourceManager
from app.ai.kernel.runtime_coordinator import RuntimeCoordinator
from app.ai.kernel.universal_verifier import UniversalVerifier
from app.ai.kernel.utils import format_voice_response
from app.ai.kernel.voice_orchestrator import VoiceOrchestrator


class KernelEngine(IKernelEngine):
    """The central AI Operating System Kernel Engine for Nova AI."""

    def __init__(self, config: Optional[KernelConfiguration] = None) -> None:
        self.config = config or KernelConfiguration()
        self.manager = KernelManager(self.config)
        self.intent_engine = IntentEngine()
        self.capability_resolver = CapabilityResolver()
        self.dynamic_planner = DynamicPlanner()
        self.resource_manager = SystemResourceManager()
        self.context_engine = ContextEngine()
        self.runtime_coordinator = RuntimeCoordinator()
        self.universal_verifier = UniversalVerifier()
        self.event_bus = EventBus()
        self.os_memory = OSMemory()
        self.copilot_integration = CopilotIntegration()
        self.security_guard = KernelSecurityGuard()
        self.metrics_tracker = KernelMetricsTracker()
        self.health_monitor = KernelHealthMonitor()
        self.voice_orchestrator = VoiceOrchestrator(kernel_engine=self)

        self.health_monitor.set_state(KernelState.IDLE)
        self.manager._state = KernelState.IDLE

    async def process_intent(
        self, query_or_request: Union[str, IntentRequest], **kwargs: Any
    ) -> IntentResponse:
        """Main kernel entry point receiving natural language queries and executing intent DAGs.

        Args:
            query_or_request: Text string or IntentRequest instance.
            **kwargs: Extra runtime options.

        Returns:
            IntentResponse containing full execution results, verification, and spoken voice response.
        """
        start_time = time.time()

        if self.manager.is_paused:
            raise KernelStateError("AI OS Kernel is currently paused.")

        if isinstance(query_or_request, str):
            request = IntentRequest(
                query=query_or_request,
                operating_mode=kwargs.get("mode", OperatingMode.VOICE),
                priority=kwargs.get("priority", PriorityLevel.NORMAL),
            )
        else:
            request = query_or_request

        self.health_monitor.set_state(KernelState.PROCESSING)

        # 1. Event Bus: publish WAKE_WORD_DETECTED or INTENT_RECEIVED
        await self.event_bus.publish("INTENT_RECEIVED", {"query": request.query, "request_id": request.request_id})

        # 2. Universal Intent Engine
        goal_data = await self.intent_engine.parse_intent(request)
        await self.os_memory.push_task(goal_data)

        # 3. Capability Resolver
        capabilities = await self.capability_resolver.resolve_capabilities(goal_data)

        # 4. Security Check
        approval_req = self.security_guard.check_approval_required(
            f"{goal_data.get('goal', '')} {request.query}", request.parameters
        )
        if approval_req and self.config.security_approval_required:
            self.metrics_tracker.record_intent(
                latency_ms=(time.time() - start_time) * 1000.0,
                success=False,
                voice=True,
                challenge=True,
            )
            self.health_monitor.set_state(KernelState.IDLE)
            return IntentResponse(
                intent_id=request.request_id,
                goal=goal_data.get("goal", ""),
                intent_type=goal_data.get("intent_type", "general"),
                capability_match=capabilities,
                status="approval_required",
                result={"reason": "Security policy checkpoint: user approval required"},
                voice_response=format_voice_response(goal_data.get("goal", ""), "approval_required"),
                latency_ms=(time.time() - start_time) * 1000.0,
            )

        # 5. Dynamic Planner
        self.health_monitor.set_state(KernelState.PLANNING)
        plan = await self.dynamic_planner.generate_plan(goal_data, capabilities)
        await self.event_bus.publish("PLAN_GENERATED", {"plan_id": plan.plan_id, "goal": plan.goal})

        # 6. Context Engine
        context = await self.context_engine.get_unified_context(request.session_id)

        # 7. Runtime Coordinator
        self.health_monitor.set_state(KernelState.EXECUTING)
        await self.event_bus.publish("MISSION_STARTED", {"goal": plan.goal, "plan_id": plan.plan_id})
        self.metrics_tracker.record_subsystem_call(plan.intent_type)

        if "software_copilot" in plan.intent_type:
            exec_output = await self.copilot_integration.handle_code_task(request.query)
        else:
            exec_output = await self.runtime_coordinator.execute_plan(plan, context)

        # 8. Universal Verification
        self.health_monitor.set_state(KernelState.VERIFYING)
        verification = await self.universal_verifier.verify_execution(
            step_title=plan.goal,
            check_spec="post_condition_assertion",
            result_data=exec_output,
        )

        status_code = "completed" if verification.verified else "failed"
        await self.event_bus.publish(
            "MISSION_COMPLETED" if verification.verified else "MISSION_FAILED",
            {"goal": plan.goal, "plan_id": plan.plan_id},
        )

        # Record action in OS Memory
        await self.os_memory.record_action("process_intent", {"goal": plan.goal, "status": status_code})

        # 9. Voice Response Synthesis
        spoken_text = format_voice_response(plan.goal, status_code, str(exec_output.get("result", "")))

        elapsed_ms = (time.time() - start_time) * 1000.0
        self.metrics_tracker.record_intent(
            latency_ms=elapsed_ms, success=verification.verified, voice=True
        )
        self.health_monitor.set_state(KernelState.IDLE)

        return IntentResponse(
            intent_id=request.request_id,
            goal=plan.goal,
            intent_type=plan.intent_type,
            capability_match=capabilities,
            execution_plan=plan,
            status=status_code,
            result=exec_output,
            verification=verification,
            voice_response=spoken_text,
            latency_ms=elapsed_ms,
        )

    async def system_snapshot(self) -> SystemSnapshot:
        """Captures hardware and workload system snapshot."""
        return await self.resource_manager.capture_snapshot()

    async def system_health(self) -> KernelHealth:
        """Retrieves system health status."""
        return self.health_monitor.check_health()

    async def active_context(self) -> ExecutionContext:
        """Retrieves active unified context."""
        return await self.context_engine.get_unified_context()

    async def kernel_metrics(self) -> KernelMetrics:
        """Retrieves telemetry metrics."""
        return self.metrics_tracker.get_metrics()

    async def pause_kernel(self) -> Dict[str, str]:
        """Pauses AI OS Kernel processing."""
        await self.manager.pause()
        self.health_monitor.set_state(KernelState.PAUSED)
        return {"status": "paused", "state": self.manager.state.value}

    async def resume_kernel(self) -> Dict[str, str]:
        """Resumes AI OS Kernel processing."""
        await self.manager.resume()
        self.health_monitor.set_state(KernelState.IDLE)
        return {"status": "resumed", "state": self.manager.state.value}
