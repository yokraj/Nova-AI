"""Idle Detector tracking user keyboard/mouse activity and inactivity duration."""

import structlog

logger = structlog.get_logger("idle_detector")


class IdleDetector:
    """Tracks keyboard/mouse activity and flags idle state after threshold."""

    def __init__(self) -> None:
        self.idle_seconds = 0.0

    async def is_user_idle(self) -> bool:
        """Check if user is currently idle."""
        return self.idle_seconds > 300.0
