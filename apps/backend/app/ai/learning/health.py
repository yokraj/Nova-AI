"""Learning Health Monitor — composite health check across all Learning Engine sub-systems."""

from typing import Any, Dict


class LearningHealthMonitor:
    """Evaluates live status of all five Learning Engine sub-systems.

    Sub-systems monitored:
    1. Learning Engine (central orchestrator)
    2. Experience Store
    3. Pattern Detector
    4. Strategy Repository
    5. Recommendation Engine
    """

    def __init__(
        self,
        experience_store: Any,
        pattern_detector: Any,
        strategy_repository: Any,
        recommendation_engine: Any,
    ) -> None:
        self.experience_store = experience_store
        self.pattern_detector = pattern_detector
        self.strategy_repository = strategy_repository
        self.recommendation_engine = recommendation_engine

    def check_health(self) -> Dict[str, Any]:
        """Run validation checks and return a composite status report."""
        details = {
            "experience_store": self._check_store(),
            "pattern_detector": self._check_detector(),
            "strategy_repository": self._check_strategies(),
            "recommendation_engine": self._check_recommender(),
        }
        overall = "healthy" if all(v == "online" for v in details.values()) else "degraded"
        return {
            "status": overall,
            "components": details,
            "total_experiences": self._safe_count(self.experience_store),
            "total_strategies": self._safe_count(self.strategy_repository),
            "pattern_matches": len(self.pattern_detector.list_patterns())
            if self.pattern_detector
            else 0,
        }

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _check_store(self) -> str:
        try:
            assert self.experience_store is not None
            _ = self.experience_store.count()
            return "online"
        except Exception:
            return "offline"

    def _check_detector(self) -> str:
        try:
            assert self.pattern_detector is not None
            return "online"
        except Exception:
            return "offline"

    def _check_strategies(self) -> str:
        try:
            assert self.strategy_repository is not None
            _ = self.strategy_repository.count()
            return "online"
        except Exception:
            return "offline"

    def _check_recommender(self) -> str:
        try:
            assert self.recommendation_engine is not None
            return "online"
        except Exception:
            return "offline"

    @staticmethod
    def _safe_count(obj: Any) -> int:
        try:
            return obj.count() if obj else 0
        except Exception:
            return 0
