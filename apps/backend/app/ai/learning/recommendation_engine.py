"""Recommendation Engine — produces actionable recommendations for engines and agents."""

import structlog
from typing import List, Optional

from app.ai.learning.configuration import LearningConfiguration
from app.ai.learning.experience_store import ExperienceStore
from app.ai.learning.models import Recommendation, RecommendationTarget
from app.ai.learning.pattern_detector import PatternDetector
from app.ai.learning.strategy_repository import StrategyRepository

logger = structlog.get_logger("recommendation_engine")


class RecommendationEngine:
    """Consults patterns and strategies to produce recommendations for other engines.

    Recommendations are issued to:
    - Planner:  which strategy and agent arrangement to use for a goal
    - Workflow:  which workflow template is reusable
    - Mission:  whether prior experience warrants fast-path execution
    - Agent:    which strategy to apply for domain-specific tasks
    - Safety:   risk classification guidance from historical approvals
    """

    def __init__(
        self,
        store: Optional[ExperienceStore] = None,
        pattern_detector: Optional[PatternDetector] = None,
        strategy_repo: Optional[StrategyRepository] = None,
        config: Optional[LearningConfiguration] = None,
    ) -> None:
        self.store = store or ExperienceStore()
        self.detector = pattern_detector or PatternDetector(store=self.store)
        self.strategies = strategy_repo or StrategyRepository()
        self.config = config or LearningConfiguration()
        self._total_generated: int = 0

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def recommend_for_goal(self, goal: str) -> List[Recommendation]:
        """Produce recommendations targeted at the Planner for a given goal."""
        recommendations: List[Recommendation] = []
        keywords = self._keywords(goal)

        # Strategy recommendation
        strategy = self.strategies.best_for_keywords(keywords)
        if strategy and strategy.success_rate >= self.config.recommendation_confidence_threshold:
            rec = Recommendation(
                target=RecommendationTarget.PLANNER,
                content=(
                    f"Use '{strategy.name}' strategy for this goal. "
                    f"Success rate: {strategy.success_rate:.0%}. "
                    f"Steps: {'; '.join(strategy.steps[:3])} …"
                ),
                strategy_id=strategy.strategy_id,
                confidence=strategy.success_rate,
                goal_context=goal,
            )
            recommendations.append(rec)
            self._total_generated += 1

        # Pattern-based recommendation
        patterns = self.detector.patterns_for_goal(goal)
        for pattern in patterns[:2]:  # top-2 patterns
            if pattern.occurrences < self.config.pattern_min_occurrences:
                continue
            rec = Recommendation(
                target=RecommendationTarget.PLANNER,
                content=(
                    f"Pattern '{pattern.name}' has been observed {pattern.occurrences} times "
                    f"with {pattern.success_rate:.0%} success. "
                    "Consider reusing its agent arrangement."
                ),
                pattern_id=pattern.pattern_id,
                confidence=pattern.success_rate,
                goal_context=goal,
            )
            recommendations.append(rec)
            self._total_generated += 1

        return recommendations

    def recommend_for_workflow(self, task: str) -> List[Recommendation]:
        """Produce workflow engine recommendations for a given task description."""
        keywords = self._keywords(task)
        strategy = self.strategies.best_for_keywords(keywords)
        recommendations: List[Recommendation] = []

        if strategy:
            rec = Recommendation(
                target=RecommendationTarget.WORKFLOW,
                content=(
                    f"Reuse '{strategy.name}' workflow template "
                    f"(success rate {strategy.success_rate:.0%}) "
                    f"for task: {task}"
                ),
                strategy_id=strategy.strategy_id,
                confidence=strategy.success_rate,
                goal_context=task,
            )
            recommendations.append(rec)
            self._total_generated += 1

        return recommendations

    def recommend_for_agent(self, agent_id: str, domain: str = "") -> List[Recommendation]:
        """Produce strategy recommendations targeted at a specific agent."""
        recommendations: List[Recommendation] = []
        strategy = self.strategies.best_strategy(domain) if domain else None

        if strategy:
            rec = Recommendation(
                target=RecommendationTarget.AGENT,
                content=(
                    f"Agent '{agent_id}' should apply '{strategy.name}' "
                    f"for {domain} tasks "
                    f"(success rate {strategy.success_rate:.0%})."
                ),
                strategy_id=strategy.strategy_id,
                confidence=strategy.success_rate,
                goal_context=domain,
            )
            recommendations.append(rec)
            self._total_generated += 1

        # Check if agent appears in successful patterns
        patterns = [
            p
            for p in self.detector.list_patterns()
            if agent_id in p.agent_ids and p.success_rate >= 0.7
        ]
        for pattern in patterns[:1]:
            rec = Recommendation(
                target=RecommendationTarget.AGENT,
                content=(
                    f"Agent '{agent_id}' excels in '{pattern.name}' pattern "
                    f"({pattern.success_rate:.0%} success rate). "
                    "Prefer this agent for similar goals."
                ),
                pattern_id=pattern.pattern_id,
                confidence=pattern.success_rate,
                goal_context=agent_id,
            )
            recommendations.append(rec)
            self._total_generated += 1

        return recommendations

    def recommend_for_safety(self, action: str) -> List[Recommendation]:
        """Produce safety policy recommendations based on historical approvals."""
        recommendations: List[Recommendation] = []
        experiences = self.store.list_experiences()

        approved_count = sum(
            1 for e in experiences if e.approval_count == 0 and e.outcome.value == "completed"
        )
        total = len(experiences)

        if total > 0 and (approved_count / total) >= 0.8:
            rec = Recommendation(
                target=RecommendationTarget.SAFETY,
                content=(
                    f"Historical data shows {approved_count / total:.0%} of missions "
                    "complete without requiring human approval. "
                    "Consider relaxing approval thresholds for low-risk actions."
                ),
                confidence=0.75,
                goal_context=action,
            )
            recommendations.append(rec)
            self._total_generated += 1

        return recommendations

    def total_recommendations_generated(self) -> int:
        """Return the cumulative count of all recommendations produced."""
        return self._total_generated

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _keywords(text: str) -> List[str]:
        """Extract meaningful keywords from a text string."""
        stop = {
            "a", "an", "the", "and", "or", "to", "of", "in", "for", "with",
            "build", "create", "make", "develop", "implement", "design", "run",
        }
        return [
            w.lower().strip(".,;:!?")
            for w in text.split()
            if w.lower() not in stop and len(w) > 2
        ]
