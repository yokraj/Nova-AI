"""Agent Learning Engine for Reusable Patterns & Recommendations.
"""

from typing import Any, Dict, List
from app.ai.agents.interfaces import IAgentLearningEngine
from app.ai.agents.models import AgentLearningRecord


class AgentLearningEngine(IAgentLearningEngine):
    """Persists successful workflow patterns, templates, and recommendations without mutating core protected logic."""

    def __init__(self) -> None:
        self._records: Dict[str, AgentLearningRecord] = {}

    def record_learning(self, pattern_name: str, steps: List[str]) -> AgentLearningRecord:
        """Persists successful workflow pattern."""
        rec = AgentLearningRecord(
            pattern_name=pattern_name,
            successful_steps=steps,
            optimizations={"recommended_parallelism": 4, "quality_check_required": True},
        )
        self._records[rec.record_id] = rec
        return rec

    def get_learned_patterns(self) -> List[AgentLearningRecord]:
        return list(self._records.values())
