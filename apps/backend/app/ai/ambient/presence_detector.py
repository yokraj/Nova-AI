"""Presence Detector tracking physical and digital user presence."""

import structlog

logger = structlog.get_logger("presence_detector")


class PresenceDetector:
    """Tracks physical and digital user presence status."""

    async def is_present(self) -> bool:
        """Check presence status."""
        return True
