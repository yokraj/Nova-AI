"""Safety Feedback — improves risk classification and policy effectiveness from history."""

import structlog
from typing import Any, Dict, List, Optional

from app.ai.learning.experience_store import ExperienceStore
from app.ai.learning.models import ExperienceOutcome

logger = structlog.get_logger("safety_feedback")


class SafetyFeedback:
    """Learns from historical approval/rejection patterns to improve the Safety Engine.

    Responsibilities:
    - Track which actions are frequently approved without issue
    - Track which actions are frequently rejected or cause failures
    - Suggest risk classification adjustments
    - Measure policy effectiveness over time
    """

    def __init__(self, store: Optional[ExperienceStore] = None) -> None:
        self.store = store or ExperienceStore()
        # action_name -> {approved: int, rejected: int}
        self._action_history: Dict[str, Dict[str, int]] = {}

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def record_action(
        self,
        action: str,
        approved: bool,
        mission_id: Optional[str] = None,
    ) -> None:
        """Record an approval decision for a specific action."""
        stats = self._action_history.setdefault(action, {"approved": 0, "rejected": 0})
        if approved:
            stats["approved"] += 1
        else:
            stats["rejected"] += 1
        logger.debug(
            "Safety action recorded",
            action=action,
            approved=approved,
            mission_id=mission_id,
        )

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def frequently_approved_actions(self, threshold: float = 0.8) -> List[str]:
        """Return actions that are approved at or above *threshold* rate."""
        result: List[str] = []
        for action, stats in self._action_history.items():
            total = stats["approved"] + stats["rejected"]
            if total == 0:
                continue
            if stats["approved"] / total >= threshold:
                result.append(action)
        return result

    def frequently_rejected_actions(self, threshold: float = 0.5) -> List[str]:
        """Return actions that are rejected at or above *threshold* rate."""
        result: List[str] = []
        for action, stats in self._action_history.items():
            total = stats["approved"] + stats["rejected"]
            if total == 0:
                continue
            if stats["rejected"] / total >= threshold:
                result.append(action)
        return result

    def policy_effectiveness(self) -> Dict[str, Any]:
        """Compute overall policy effectiveness from all recorded actions."""
        total_approved = sum(s["approved"] for s in self._action_history.values())
        total_rejected = sum(s["rejected"] for s in self._action_history.values())
        total = total_approved + total_rejected

        experiences = self.store.list_experiences()
        mission_success = sum(
            1 for e in experiences if e.outcome == ExperienceOutcome.COMPLETED
        )
        mission_total = len(experiences)

        return {
            "total_actions_evaluated": total,
            "approval_rate": round(total_approved / total, 4) if total else 0.0,
            "rejection_rate": round(total_rejected / total, 4) if total else 0.0,
            "mission_success_rate": (
                round(mission_success / mission_total, 4) if mission_total else 0.0
            ),
            "frequently_approved": self.frequently_approved_actions(),
            "frequently_rejected": self.frequently_rejected_actions(),
        }

    def risk_classification_suggestions(self) -> List[str]:
        """Generate risk reclassification suggestions from approval history."""
        suggestions: List[str] = []
        approved = self.frequently_approved_actions(threshold=0.9)
        rejected = self.frequently_rejected_actions(threshold=0.7)

        for action in approved:
            suggestions.append(
                f"Action '{action}' is approved {self._approval_rate(action):.0%} "
                "of the time. Consider lowering its risk classification to reduce friction."
            )

        for action in rejected:
            suggestions.append(
                f"Action '{action}' is rejected {self._rejection_rate(action):.0%} "
                "of the time. Consider marking it HIGH_RISK by default."
            )

        return suggestions or ["Risk classifications appear well-calibrated."]

    def autonomy_recommendations(self) -> List[str]:
        """Recommend which actions can safely be auto-approved in future."""
        safe_actions = self.frequently_approved_actions(threshold=0.95)
        if not safe_actions:
            return ["Insufficient data to recommend autonomous approval expansions."]
        return [
            f"Action '{a}' qualifies for autonomous approval (consent bypass)."
            for a in safe_actions[:5]
        ]

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _approval_rate(self, action: str) -> float:
        stats = self._action_history.get(action, {"approved": 0, "rejected": 0})
        total = stats["approved"] + stats["rejected"]
        return stats["approved"] / total if total else 0.0

    def _rejection_rate(self, action: str) -> float:
        stats = self._action_history.get(action, {"approved": 0, "rejected": 0})
        total = stats["approved"] + stats["rejected"]
        return stats["rejected"] / total if total else 0.0
