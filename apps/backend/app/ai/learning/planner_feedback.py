"""Planner Feedback — provides the Intelligent Planner with history-aware recommendations."""

import structlog
from typing import Any, Dict, List, Optional

from app.ai.learning.experience_store import ExperienceStore
from app.ai.learning.models import ExperienceOutcome
from app.ai.learning.recommendation_engine import RecommendationEngine
from app.ai.learning.strategy_repository import StrategyRepository

logger = structlog.get_logger("planner_feedback")


class PlannerFeedback:
    """Feeds historical success data back into the Intelligent Planner.

    The planner can call :meth:`enrich_plan_request` at plan-time to receive:
    - Prior success rates for similar goals
    - Recommended strategies and agent arrangements
    - Historical execution time estimates
    - Flagged failure patterns to avoid
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

    def enrich_plan_request(self, goal: str) -> Dict[str, Any]:
        """Return a dict of learning-derived hints to augment a planning request.

        Args:
            goal: Natural language planning goal.

        Returns:
            Dict with ``success_rate``, ``avg_duration_seconds``,
            ``recommendations``, ``agent_performance``, ``failure_warnings``.
        """
        similar = self._find_similar_experiences(goal)
        success_rate = self._compute_success_rate(similar)
        avg_duration = self._compute_avg_duration(similar)
        recommendations = self.recommender.recommend_for_goal(goal)
        agent_performance = self._agent_performance(similar)
        failure_warnings = self._failure_warnings(goal)

        result = {
            "success_rate": success_rate,
            "avg_duration_seconds": avg_duration,
            "similar_missions_count": len(similar),
            "recommendations": [r.content for r in recommendations],
            "agent_performance": agent_performance,
            "failure_warnings": failure_warnings,
        }
        logger.debug("Planner feedback enriched", goal=goal, similar=len(similar))
        return result

    def historical_success_rate(self, domain_keyword: str) -> float:
        """Return the success rate for all experiences containing the keyword."""
        matching = [
            e for e in self.store.list_experiences()
            if domain_keyword.lower() in e.goal.lower()
        ]
        if not matching:
            return 0.5  # Neutral prior when no data
        completed = sum(1 for e in matching if e.outcome == ExperienceOutcome.COMPLETED)
        return round(completed / len(matching), 4)

    def recommended_agents_for_goal(self, goal: str) -> List[str]:
        """Return agent IDs that historically performed well on similar goals."""
        similar = self._find_similar_experiences(goal)
        successful = [e for e in similar if e.outcome == ExperienceOutcome.COMPLETED]
        agent_freq: Dict[str, int] = {}
        for exp in successful:
            for agent in exp.agents_used:
                agent_freq[agent] = agent_freq.get(agent, 0) + 1
        return sorted(agent_freq, key=agent_freq.get, reverse=True)[:3]  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _find_similar_experiences(self, goal: str) -> List[Any]:
        keywords = goal.lower().split()[:3]
        return self.store.experiences_for_goal_keywords(keywords)

    @staticmethod
    def _compute_success_rate(experiences: List[Any]) -> float:
        if not experiences:
            return 0.5
        completed = sum(1 for e in experiences if e.outcome == ExperienceOutcome.COMPLETED)
        return round(completed / len(experiences), 4)

    @staticmethod
    def _compute_avg_duration(experiences: List[Any]) -> float:
        if not experiences:
            return 0.0
        durations = [e.duration_seconds for e in experiences]
        return round(sum(durations) / len(durations), 2)

    @staticmethod
    def _agent_performance(experiences: List[Any]) -> Dict[str, float]:
        """Return per-agent participation success rates from a set of experiences."""
        agent_totals: Dict[str, int] = {}
        agent_wins: Dict[str, int] = {}
        for exp in experiences:
            for agent in exp.agents_used:
                agent_totals[agent] = agent_totals.get(agent, 0) + 1
                if exp.outcome == ExperienceOutcome.COMPLETED:
                    agent_wins[agent] = agent_wins.get(agent, 0) + 1
        return {
            agent: round(agent_wins.get(agent, 0) / total, 4)
            for agent, total in agent_totals.items()
        }

    def _failure_warnings(self, goal: str) -> List[str]:
        """List failure patterns observed for similar goals."""
        keywords = goal.lower().split()[:3]
        failed = [
            e
            for e in self.store.experiences_for_goal_keywords(keywords)
            if e.outcome == ExperienceOutcome.FAILED
        ]
        warnings: List[str] = []
        if failed:
            warnings.append(
                f"{len(failed)} similar mission(s) previously failed. "
                "Ensure prerequisites are met and agents are available."
            )
        return warnings
