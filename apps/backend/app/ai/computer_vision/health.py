"""Vision Health Monitor performing diagnostic system health checks.
"""

import time
from typing import List
from app.ai.computer_vision.models import VisionHealth, VisionState


class VisionHealthMonitor:
    """Monitors health of Computer Vision Engine and sub-components."""

    def __init__(self) -> None:
        self._state = VisionState.IDLE

    def set_state(self, state: VisionState) -> None:
        """Updates active vision state."""
        self._state = state

    def check_health(self) -> VisionHealth:
        """Performs health diagnostic check.

        Returns:
            VisionHealth model instance.
        """
        loaded_profiles: List[str] = [
            "Windows Explorer", "Chrome", "Edge", "Firefox", "VS Code",
            "Visual Studio", "Cursor", "Antigravity", "PyCharm", "Android Studio",
            "Excel", "Word", "PowerPoint", "Outlook", "Teams", "Photoshop",
            "Blender", "Terminal", "Settings"
        ]

        return VisionHealth(
            is_healthy=self._state != VisionState.ERROR,
            vision_state=self._state,
            active_monitors_count=2,
            loaded_profiles=loaded_profiles,
            timestamp=time.time(),
        )
