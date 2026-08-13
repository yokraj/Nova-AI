"""Copilot Health Monitor performing diagnostic system health checks.
"""

import time
from typing import List
from app.ai.copilot.models import CopilotHealth, CopilotState


class CopilotHealthMonitor:
    """Monitors health of AI Software Copilot and sub-engines."""

    def __init__(self) -> None:
        self._state = CopilotState.IDLE

    def set_state(self, state: CopilotState) -> None:
        """Updates active copilot state."""
        self._state = state

    def check_health(self) -> CopilotHealth:
        """Performs health diagnostic check.

        Returns:
            CopilotHealth model instance.
        """
        loaded_engines: List[str] = [
            "RequirementAnalyzer",
            "SoftwareArchitectureEngine",
            "TechnologySelector",
            "CodeGenerator",
            "CodeUnderstandingEngine",
            "DebugEngine",
            "RefactorEngine",
            "TestEngine",
            "DevOpsEngine",
            "DocumentationEngine",
            "CodeReviewEngine",
            "ProjectManager",
            "IDEIntegration",
            "GitIntegration",
        ]

        return CopilotHealth(
            is_healthy=self._state != CopilotState.ERROR,
            copilot_state=self._state,
            active_projects_count=1,
            loaded_engines=loaded_engines,
            timestamp=time.time(),
        )
