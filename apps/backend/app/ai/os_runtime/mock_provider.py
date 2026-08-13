"""Mock OS Runtime Provider for testing and offline simulation.
"""

from typing import Any, Dict
from app.ai.os_runtime.models import OSBootDiagnostic, OSHealth, OSState


class MockOSRuntimeProvider:
    """Mock OS runtime provider simulating OS boot, lifecycle transitions, and diagnostic metrics."""

    async def mock_boot_system(self) -> OSBootDiagnostic:
        """Simulates system boot sequence."""
        return OSBootDiagnostic(
            duration_sec=0.15,
            subsystems_loaded=["Kernel", "Models", "Voice", "Desktop Automation", "OS Daemon"],
            success=True,
        )

    async def mock_get_health(self) -> OSHealth:
        """Simulates OS health status."""
        return OSHealth(
            is_healthy=True,
            os_state=OSState.RUNNING,
            subsystems_healthy_count=25,
            total_subsystems=25,
        )
