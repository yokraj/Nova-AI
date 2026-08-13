"""Mission Feedback — stores and aggregates mission-level performance metrics."""

import structlog
from typing import Any, Dict, List, Optional

from app.ai.learning.experience_store import ExperienceStore
from app.ai.learning.models import ExperienceOutcome

logger = structlog.get_logger("mission_feedback")


class MissionFeedback:
    """Aggregates mission-level KPIs to inform the Mission Engine of historical patterns.

    Tracked metrics per mission:
    - Completion rate
    - Average execution duration
    - Recovery count
    - User satisfaction score
    - Approval (interruption) frequency
    """

    def __init__(self, store: Optional[ExperienceStore] = None) -> None:
        self.store = store or ExperienceStore()
        # mission_id -> most recent experience metadata
        self._mission_index: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def record_mission(
        self,
        mission_id: str,
        goal: str,
        outcome: str,
        duration_seconds: float,
        recovery_count: int = 0,
        approval_count: int = 0,
        user_satisfaction: float = 1.0,
    ) -> None:
        """Record key performance data for a completed or failed mission."""
        self._mission_index[mission_id] = {
            "goal": goal,
            "outcome": outcome,
            "duration_seconds": duration_seconds,
            "recovery_count": recovery_count,
            "approval_count": approval_count,
            "user_satisfaction": user_satisfaction,
        }
        logger.debug("Mission feedback recorded", mission_id=mission_id, outcome=outcome)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_mission_record(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Return the performance record for a specific mission."""
        return self._mission_index.get(mission_id)

    def completion_rate(self) -> float:
        """Compute overall mission completion rate from the experience store."""
        experiences = self.store.list_experiences()
        if not experiences:
            return 0.0
        completed = sum(1 for e in experiences if e.outcome == ExperienceOutcome.COMPLETED)
        return round(completed / len(experiences), 4)

    def average_duration(self) -> float:
        """Compute average mission execution duration in seconds."""
        experiences = self.store.list_experiences()
        if not experiences:
            return 0.0
        return round(
            sum(e.duration_seconds for e in experiences) / len(experiences), 2
        )

    def average_satisfaction(self) -> float:
        """Compute average user satisfaction across all missions."""
        experiences = self.store.list_experiences()
        if not experiences:
            return 0.0
        return round(
            sum(e.user_satisfaction for e in experiences) / len(experiences), 4
        )

    def total_recoveries(self) -> int:
        """Return the total number of recovery attempts across all missions."""
        return sum(e.recovery_count for e in self.store.list_experiences())

    def total_approvals(self) -> int:
        """Return total human approval interventions across all missions."""
        return sum(e.approval_count for e in self.store.list_experiences())

    def summary(self) -> Dict[str, Any]:
        """Return a comprehensive mission performance summary."""
        return {
            "completion_rate": self.completion_rate(),
            "average_duration_seconds": self.average_duration(),
            "average_satisfaction": self.average_satisfaction(),
            "total_recoveries": self.total_recoveries(),
            "total_approvals": self.total_approvals(),
            "total_missions": self.store.count(),
        }

    def improvement_opportunities(self) -> List[str]:
        """Identify areas where mission execution can be improved."""
        suggestions: List[str] = []
        rate = self.completion_rate()
        avg_dur = self.average_duration()
        total_rec = self.total_recoveries()
        total_app = self.total_approvals()

        if rate < 0.7:
            suggestions.append(
                f"Low completion rate ({rate:.0%}). "
                "Improve agent assignments and pre-flight validation."
            )
        if avg_dur > 300:
            suggestions.append(
                f"Average mission duration ({avg_dur:.0f}s) is high. "
                "Consider splitting missions into smaller objectives."
            )
        if total_rec > 0:
            suggestions.append(
                f"{total_rec} recovery attempt(s) recorded. "
                "Add more robust error handling and checkpoint strategies."
            )
        if total_app > 5:
            suggestions.append(
                f"{total_app} human approval(s) requested. "
                "Review risk classification thresholds to reduce interruptions."
            )

        return suggestions or ["Mission performance is within healthy bounds."]
