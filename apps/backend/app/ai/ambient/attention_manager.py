"""Attention Manager estimating user cognitive workload and focus area."""

import structlog

logger = structlog.get_logger("attention_manager")


class AttentionManager:
    """Estimates user cognitive focus and workload intensity."""

    async def get_workload_level(self) -> str:
        """Get cognitive workload estimate."""
        return "high_focus"
