"""Telemetry metrics collector for Autonomous Self-Improvement & Adaptive Intelligence Engine.
"""

import time
from app.ai.self_improvement.models import SelfImprovementMetrics


class SelfImprovementMetricsTracker:
    """Collects evaluations, optimizations applied, experience packages distilled, and regressions prevented."""

    def __init__(self) -> None:
        self._total_evaluations = 0
        self._optimizations_applied = 0
        self._experiences_distilled = 0
        self._regressions_prevented = 0

    def record_evaluation(self) -> None:
        """Records evaluation pass."""
        self._total_evaluations += 1

    def record_optimization(self) -> None:
        """Records applied optimization."""
        self._optimizations_applied += 1

    def record_experience_distillation(self) -> None:
        """Records experience distillation."""
        self._experiences_distilled += 1

    def record_regression_prevented(self) -> None:
        """Records regression prevented."""
        self._regressions_prevented += 1

    def get_metrics(self) -> SelfImprovementMetrics:
        """Returns current SelfImprovementMetrics snapshot."""
        return SelfImprovementMetrics(
            total_evaluations=self._total_evaluations,
            optimizations_applied=self._optimizations_applied,
            experiences_distilled=self._experiences_distilled,
            regressions_prevented=self._regressions_prevented,
            timestamp=time.time(),
        )
