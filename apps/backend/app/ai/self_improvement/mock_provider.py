"""Mock Self-Improvement Provider returning deterministic test responses for offline tests and CI.
"""

from typing import Any, Dict, List
from app.ai.self_improvement.models import (
    AgentScorecard,
    BenchmarkReport,
    EvaluationCycle,
    QualityDiagnosticReport,
    RegressionStatus,
)


class MockSelfImprovementProvider:
    """Mock Self-Improvement Provider returning deterministic test responses."""

    async def mock_self_improve(self) -> Dict[str, Any]:
        return {
            "status": "SUCCESS",
            "optimizations_applied": 3,
            "latency_reduction_pct": 22.5,
        }

    async def mock_benchmark(self) -> BenchmarkReport:
        return BenchmarkReport(
            cycle=EvaluationCycle.DAILY,
            agent_scorecards=[AgentScorecard(agent_name="Mock Agent", role="software_engineer")],
            overall_score=0.98,
        )

    async def mock_quality(self) -> QualityDiagnosticReport:
        return QualityDiagnosticReport(status=RegressionStatus.NORMAL)
