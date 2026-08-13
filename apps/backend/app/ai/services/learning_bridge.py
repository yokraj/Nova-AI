"""Learning Bridge feeding workflow success rates, durations, CAPTCHAs, and outcomes to Learning Engine."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("learning_bridge")


class LearningBridge:
    """Records service workflow execution experience to Learning Engine."""

    def __init__(self, memory_engine: Any = None) -> None:
        self.memory = memory_engine

    async def record_workflow_experience(
        self,
        service_id: str,
        success: bool,
        duration_seconds: float,
        metrics: Dict[str, Any],
    ) -> None:
        """Feed service metrics and outcome back to Learning Engine."""
        logger.info("LearningBridge recording workflow outcome", service_id=service_id, success=success, duration=duration_seconds)
        try:
            from app.ai.learning.learning_engine import LearningEngine
            le = LearningEngine()
            await le.learn_from_mission(
                mission_id=f"ms_service_{service_id}",
                mission_result={
                    "goal": f"Execute service workflow '{service_id}'",
                    "status": "completed" if success else "failed",
                    "duration_seconds": duration_seconds,
                    "agents_used": ["service_automation"],
                    "metrics": metrics,
                },
            )
        except Exception as e:
            logger.debug("Learning Engine bridge fallback", error=str(e))
