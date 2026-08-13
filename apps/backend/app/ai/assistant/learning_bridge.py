"""Learning Bridge feeding personal habits, work hours, and routines to Learning Engine."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("assistant_learning_bridge")


class LearningBridge:
    """Records user life habits and work hour preferences to Learning Engine."""

    async def record_user_preference(self, key: str, value: Any) -> None:
        """Record user preference into Learning Engine."""
        logger.info("LearningBridge recording user preference", key=key, value=value)
        try:
            from app.ai.learning.learning_engine import LearningEngine
            le = LearningEngine()
            await le.learn_from_mission(
                mission_id=f"ms_preference_{key}",
                mission_result={
                    "goal": f"Record user preference '{key}'",
                    "status": "completed",
                    "preference_key": key,
                    "preference_value": value,
                },
            )
        except Exception as e:
            logger.debug("Learning Engine bridge fallback", error=str(e))
