"""Health Manager tracking personal wellness metrics, hydration, and break reminders."""

import structlog

from app.ai.assistant.models import HealthSnapshot

logger = structlog.get_logger("health_manager")


class HealthManager:
    """Tracks composite health, hydration, steps, and wellness breaks."""

    def __init__(self) -> None:
        self._snapshot = HealthSnapshot(water_intake_ml=1500, sleep_hours=7.5, steps_count=6400)

    async def get_health_snapshot(self) -> HealthSnapshot:
        """Get current health snapshot."""
        return self._snapshot

    async def log_water(self, amount_ml: int = 250) -> int:
        """Log hydration intake."""
        self._snapshot.water_intake_ml += amount_ml
        logger.info("Logged water intake", total_ml=self._snapshot.water_intake_ml)
        return self._snapshot.water_intake_ml
