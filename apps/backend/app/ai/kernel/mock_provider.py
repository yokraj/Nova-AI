"""Mock Kernel Provider for offline unit tests and CI integration.
"""

from typing import Any, Dict
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
    PlanNode,
    PriorityLevel,
    SystemSnapshot,
    VerificationResult,
)


class MockKernelProvider:
    """Mock Kernel Provider returning deterministic test data."""

    async def process_intent(self, request: IntentRequest) -> IntentResponse:
        """Returns deterministic IntentResponse."""
        query = request.query if isinstance(request, IntentRequest) else str(request)
        return IntentResponse(
            intent_id="mock_intent_01",
            goal=query,
            intent_type="mock_testing",
            capability_match=CapabilityMatch(agents=["mock_agent"], execution_runtime="local_async"),
            execution_plan=ExecutionPlan(
                goal=query,
                nodes=[
                    PlanNode(
                        title=f"Mock execute {query}",
                        action_type="mock_action",
                        subsystem="mock_subsystem",
                    )
                ],
            ),
            status="completed",
            result={"status": "mock_success", "query": query},
            verification=VerificationResult(verified=True, status="SUCCESS", checks_performed=["mock_check"]),
            voice_response=f"Mock response for: {query}",
            latency_ms=5.0,
        )

    async def capture_snapshot(self) -> SystemSnapshot:
        """Returns mock SystemSnapshot."""
        return SystemSnapshot(
            cpu_percent=10.0,
            ram_percent=30.0,
            ram_used_mb=2048.0,
            ram_total_mb=16384.0,
            gpu_percent=0.0,
            gpu_memory_mb=0.0,
            disk_percent=25.0,
            battery_percent=100.0,
            network_status="ONLINE",
            active_models=["mock_model"],
            active_missions_count=1,
            running_agents_count=2,
            task_queue_length=0,
            health_status="HEALTHY",
        )

    async def check_health(self) -> KernelHealth:
        """Returns mock KernelHealth."""
        return KernelHealth(
            is_healthy=True,
            kernel_state=KernelState.IDLE,
            cpu_percent=10.0,
            ram_percent=30.0,
            active_subsystems=["MockSubsystem"],
            event_bus_active=True,
            memory_health="OK",
        )
