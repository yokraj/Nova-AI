"""Workflow Feedback — ranks, flags, and optimises workflow templates from experience."""

import structlog
from typing import Any, Dict, List, Optional

from app.ai.learning.experience_store import ExperienceStore
from app.ai.learning.models import ExperienceOutcome
from app.ai.learning.recommendation_engine import RecommendationEngine
from app.ai.learning.strategy_repository import StrategyRepository

logger = structlog.get_logger("workflow_feedback")


class WorkflowFeedback:
    """Provides the Workflow Engine with learning-derived optimisations.

    Capabilities:
    - Rank reusable workflow templates by historical completion rate
    - Flag unreliable workflows that fail repeatedly
    - Suggest step-level optimisations (parallelism, caching)
    - Recommend the best workflow for a given task
    """

    def __init__(
        self,
        store: Optional[ExperienceStore] = None,
        strategy_repo: Optional[StrategyRepository] = None,
        recommendation_engine: Optional[RecommendationEngine] = None,
    ) -> None:
        self.store = store or ExperienceStore()
        self.strategy_repo = strategy_repo or StrategyRepository()
        self.recommender = recommendation_engine or RecommendationEngine(
            store=self.store, strategy_repo=self.strategy_repo
        )
        # workflow_id -> {completed: int, failed: int, total_duration: float}
        self._workflow_stats: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def update_from_store(self) -> None:
        """Rebuild workflow statistics from the experience store."""
        self._workflow_stats.clear()
        for exp in self.store.list_experiences():
            if exp.workflow_id:
                self._record_workflow_outcome(
                    exp.workflow_id, exp.outcome, exp.duration_seconds
                )

    def ranked_workflows(self) -> List[Dict[str, Any]]:
        """Return all tracked workflows ranked by success rate (highest first)."""
        ranked: List[Dict[str, Any]] = []
        for wf_id, stats in self._workflow_stats.items():
            total = stats["completed"] + stats["failed"]
            rate = stats["completed"] / total if total > 0 else 0.0
            avg_dur = stats["total_duration"] / total if total > 0 else 0.0
            ranked.append(
                {
                    "workflow_id": wf_id,
                    "success_rate": round(rate, 4),
                    "avg_duration_seconds": round(avg_dur, 2),
                    "total_runs": total,
                }
            )
        return sorted(ranked, key=lambda x: x["success_rate"], reverse=True)

    def unreliable_workflows(self, threshold: float = 0.4) -> List[str]:
        """Return workflow IDs whose success rate falls below *threshold*."""
        unreliable: List[str] = []
        for wf_id, stats in self._workflow_stats.items():
            total = stats["completed"] + stats["failed"]
            if total < 2:
                continue
            rate = stats["completed"] / total
            if rate < threshold:
                unreliable.append(wf_id)
        return unreliable

    def best_workflow_for_task(self, task: str) -> Dict[str, Any]:
        """Return the recommended workflow template for a task description."""
        recommendations = self.recommender.recommend_for_workflow(task)
        if recommendations:
            rec = recommendations[0]
            return {
                "recommendation": rec.content,
                "confidence": rec.confidence,
                "strategy_id": rec.strategy_id,
            }
        # Fallback to highest-ranked tracked workflow
        ranked = self.ranked_workflows()
        if ranked:
            best = ranked[0]
            return {
                "recommendation": (
                    f"Reuse workflow '{best['workflow_id']}' "
                    f"(success rate {best['success_rate']:.0%})."
                ),
                "confidence": best["success_rate"],
                "workflow_id": best["workflow_id"],
            }
        return {"recommendation": "No historical workflow data available.", "confidence": 0.0}

    def optimisation_suggestions(self, workflow_id: str) -> List[str]:
        """Generate step-level optimisation suggestions for a workflow."""
        stats = self._workflow_stats.get(workflow_id)
        if not stats:
            return ["No data available for this workflow."]

        suggestions: List[str] = []
        total = stats["completed"] + stats["failed"]
        rate = stats["completed"] / total if total > 0 else 0.0
        avg_dur = stats["total_duration"] / total if total > 0 else 0.0

        if avg_dur > 120:
            suggestions.append(
                f"Workflow '{workflow_id}' averages {avg_dur:.0f}s. "
                "Consider parallelising independent steps."
            )
        if rate < 0.7:
            suggestions.append(
                f"Workflow '{workflow_id}' has a {rate:.0%} success rate. "
                "Add pre-flight validation and retry policies."
            )
        if rate >= 0.9:
            suggestions.append(
                f"Workflow '{workflow_id}' is highly reliable ({rate:.0%}). "
                "Promote it as a reusable template."
            )

        return suggestions or ["Workflow performance is within acceptable bounds."]

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _record_workflow_outcome(
        self, workflow_id: str, outcome: ExperienceOutcome, duration: float
    ) -> None:
        stats = self._workflow_stats.setdefault(
            workflow_id, {"completed": 0, "failed": 0, "total_duration": 0.0}
        )
        if outcome == ExperienceOutcome.COMPLETED:
            stats["completed"] += 1
        else:
            stats["failed"] += 1
        stats["total_duration"] += duration
