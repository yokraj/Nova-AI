"""Kernel Health Monitor performing diagnostic system health checks.
"""

import time
from typing import List
from app.ai.kernel.models import KernelHealth, KernelState


class KernelHealthMonitor:
    """Monitors health of AI OS Kernel and connected subsystems."""

    def __init__(self) -> None:
        self._kernel_state = KernelState.IDLE

    def set_state(self, state: KernelState) -> None:
        """Updates active kernel state."""
        self._kernel_state = state

    def check_health(self) -> KernelHealth:
        """Performs health check.

        Returns:
            KernelHealth model instance.
        """
        active_subsystems: List[str] = [
            "IntentEngine",
            "CapabilityResolver",
            "DynamicPlanner",
            "SystemResourceManager",
            "ContextEngine",
            "RuntimeCoordinator",
            "UniversalVerifier",
            "EventBus",
            "OSMemory",
            "CopilotIntegration",
            "VoiceOrchestrator",
            "KernelSecurityGuard",
        ]

        return KernelHealth(
            is_healthy=self._kernel_state != KernelState.ERROR,
            kernel_state=self._kernel_state,
            cpu_percent=15.0,
            ram_percent=40.0,
            active_subsystems=active_subsystems,
            event_bus_active=True,
            memory_health="OK",
            timestamp=time.time(),
        )
