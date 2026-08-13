"""Experience Manager — builds Experience objects from mission result dictionaries."""

import structlog
from typing import Any, Dict, List, Optional

from app.ai.learning.experience_store import ExperienceStore
from app.ai.learning.models import Experience, ExperienceOutcome, ExperienceType

logger = structlog.get_logger("experience_manager")


class ExperienceManager:
    """Translates raw mission/workflow result dictionaries into stored Experience records.

    This is the entry-point for all data flowing *into* the learning engine.
    It normalises heterogeneous result payloads coming from MissionEngine,
    WorkflowEngine, and SafetyEngine into a canonical Experience.
    """

    def __init__(self, store: Optional[ExperienceStore] = None) -> None:
        self.store = store or ExperienceStore()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def build_experience(
        self,
        mission_id: str,
        goal: str,
        result: Dict[str, Any],
    ) -> Experience:
        """Construct an Experience from a mission result dict and persist it.

        Expected result keys (all optional, sensible defaults applied):
          - ``status``:          "success" | "failed" | "recovered" | "cancelled"
          - ``duration_seconds``: float
          - ``agents_used``:      List[str]
          - ``workflow_id``:      str
          - ``recovery_count``:  int
          - ``approval_count``:  int
          - ``user_satisfaction``: float (0.0–1.0)
        """
        outcome = self._parse_outcome(result.get("status", "failed"))
        exp_type = self._derive_type(outcome, result)

        experience = Experience(
            mission_id=mission_id,
            goal=goal,
            experience_type=exp_type,
            outcome=outcome,
            duration_seconds=float(result.get("duration_seconds", 0.0)),
            agents_used=list(result.get("agents_used", [])),
            workflow_id=result.get("workflow_id"),
            recovery_count=int(result.get("recovery_count", 0)),
            approval_count=int(result.get("approval_count", 0)),
            user_satisfaction=float(result.get("user_satisfaction", 1.0)),
            metadata=result.get("metadata", {}),
        )

        self.store.save_experience(experience)
        logger.info(
            "Built and stored experience",
            experience_id=experience.experience_id,
            mission_id=mission_id,
            outcome=outcome.value,
        )
        return experience

    def build_many(self, records: List[Dict[str, Any]]) -> List[Experience]:
        """Batch-build experiences from a list of raw result dicts."""
        return [
            self.build_experience(
                mission_id=r.get("mission_id", "unknown"),
                goal=r.get("goal", ""),
                result=r,
            )
            for r in records
        ]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_outcome(status: str) -> ExperienceOutcome:
        """Map a raw status string to an ExperienceOutcome enum value."""
        mapping = {
            "success": ExperienceOutcome.COMPLETED,
            "completed": ExperienceOutcome.COMPLETED,
            "failed": ExperienceOutcome.FAILED,
            "failure": ExperienceOutcome.FAILED,
            "recovered": ExperienceOutcome.RECOVERED,
            "recovery": ExperienceOutcome.RECOVERED,
            "cancelled": ExperienceOutcome.CANCELLED,
            "canceled": ExperienceOutcome.CANCELLED,
        }
        return mapping.get(status.lower(), ExperienceOutcome.FAILED)

    @staticmethod
    def _derive_type(
        outcome: ExperienceOutcome, result: Dict[str, Any]
    ) -> ExperienceType:
        """Derive an ExperienceType from the outcome and supplementary result data."""
        if result.get("recovery_count", 0) > 0:
            return ExperienceType.RECOVERY
        if outcome == ExperienceOutcome.COMPLETED:
            return ExperienceType.SUCCESS
        if outcome == ExperienceOutcome.FAILED:
            return ExperienceType.FAILURE
        if outcome == ExperienceOutcome.CANCELLED:
            return ExperienceType.PARTIAL
        return ExperienceType.PARTIAL
