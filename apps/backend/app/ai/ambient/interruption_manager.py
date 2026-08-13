"""Interruption Manager enforcing Do-Not-Disturb and proactive notification gating."""

import structlog

from app.ai.ambient.models import InterruptionPolicy

logger = structlog.get_logger("interruption_manager")


class InterruptionManager:
    """Enforces Do-Not-Disturb and smart notification gating during active meetings or focus blocks."""

    async def should_interrupt(self, in_meeting: bool = False, is_critical: bool = False) -> bool:
        """Determine whether proactive alert should interrupt user."""
        if in_meeting and not is_critical:
            logger.info("Suppressed proactive interruption due to active meeting (Do-Not-Disturb)")
            return False
        return True
