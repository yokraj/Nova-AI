"""HealthProvider reporting agent health telemetry metrics.
"""

import time
from typing import Any, Dict


class HealthProvider:
    """Calculates and exposes health metrics and runtime metadata."""

    def __init__(self, agent: Any) -> None:
        """Initializes HealthProvider.

        Args:
            agent: The active SoftwareEngineerAgent instance.
        """
        self.agent = agent
        self._start_time = time.time()

    def get_health(self) -> Dict[str, Any]:
        """Compiles health metrics dictionary.

        Returns:
            Dictionary containing health parameters.
        """
        uptime = time.time() - self._start_time
        workspace_loaded = bool(self.agent.workspace_manager.current_workspace())
        active_tasks_count = len(self.agent.session.active_tasks)

        return {
            "status": self.agent.state.value,
            "uptime": uptime,
            "workspace_loaded": workspace_loaded,
            "active_tasks": active_tasks_count,
            "memory_usage_placeholder": 0.0,
        }
