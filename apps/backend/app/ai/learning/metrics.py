"""Learning Metrics Tracker — collects and computes all Learning Engine KPIs."""

from typing import Any, Dict

from app.ai.learning.models import LearningMetrics


class LearningMetricsTracker:
    """Telemetry collector tracking all eight Learning Engine KPIs.

    KPIs tracked:
    1. Total experiences stored
    2. Success rate across experiences
    3. Failure rate across experiences
    4. Number of learned (stored) strategies
    5. Pattern match count
    6. Total recommendations generated
    7. Knowledge reuse percentage (strategies with usage_count > 0)
    8. Agent learning score (average cross-agent success depth)
    """

    def __init__(self) -> None:
        self._experiences_count: int = 0
        self._success_count: int = 0
        self._failure_count: int = 0
        self._strategies_count: int = 0
        self._pattern_matches: int = 0
        self._recommendations_count: int = 0
        self._reusable_strategies: int = 0
        self._agent_learning_score: float = 0.0

    # ------------------------------------------------------------------
    # Counters
    # ------------------------------------------------------------------

    def record_experience(self, success: bool) -> None:
        """Increment experience and outcome counters."""
        self._experiences_count += 1
        if success:
            self._success_count += 1
        else:
            self._failure_count += 1

    def record_pattern_match(self) -> None:
        """Increment the pattern match counter."""
        self._pattern_matches += 1

    def record_recommendation(self) -> None:
        """Increment the recommendation generated counter."""
        self._recommendations_count += 1

    # ------------------------------------------------------------------
    # Setters (updated by the Learning Engine after each learn cycle)
    # ------------------------------------------------------------------

    def set_strategies_count(self, count: int) -> None:
        """Set the total number of stored strategies."""
        self._strategies_count = count

    def set_reusable_strategies(self, count: int) -> None:
        """Set the count of strategies with usage_count > 0."""
        self._reusable_strategies = count

    def set_agent_learning_score(self, score: float) -> None:
        """Update the average agent learning score."""
        self._agent_learning_score = round(score, 4)

    def set_recommendations_count(self, count: int) -> None:
        """Sync with the recommendation engine's cumulative counter."""
        self._recommendations_count = count

    def set_pattern_matches(self, count: int) -> None:
        """Sync with the pattern detector's result count."""
        self._pattern_matches = count

    # ------------------------------------------------------------------
    # Aggregates
    # ------------------------------------------------------------------

    def success_rate(self) -> float:
        """Compute current success rate."""
        if self._experiences_count == 0:
            return 0.0
        return round(self._success_count / self._experiences_count, 4)

    def failure_rate(self) -> float:
        """Compute current failure rate."""
        if self._experiences_count == 0:
            return 0.0
        return round(self._failure_count / self._experiences_count, 4)

    def knowledge_reuse_pct(self) -> float:
        """Compute percentage of strategies that have been reused at least once."""
        if self._strategies_count == 0:
            return 0.0
        return round(self._reusable_strategies / self._strategies_count, 4)

    def snapshot(self) -> LearningMetrics:
        """Return a Pydantic LearningMetrics snapshot."""
        return LearningMetrics(
            total_experiences=self._experiences_count,
            success_rate=self.success_rate(),
            failure_rate=self.failure_rate(),
            learned_strategies=self._strategies_count,
            pattern_matches=self._pattern_matches,
            recommendations_generated=self._recommendations_count,
            knowledge_reuse_pct=self.knowledge_reuse_pct(),
            agent_learning_score=self._agent_learning_score,
        )

    def dump_summary(self) -> Dict[str, Any]:
        """Return a plain-dict summary of all learning KPIs."""
        m = self.snapshot()
        return m.model_dump(mode="json")
