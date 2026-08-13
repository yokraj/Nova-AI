"""Skill Memory tracking execution statistics, failure history, and performance preferences.
"""

from typing import Dict, List
from app.ai.skills.interfaces import ISkillMemory
from app.ai.skills.models import SkillTelemetry


class SkillMemory(ISkillMemory):
    """Stores telemetry, failure counts, and execution statistics per skill."""

    def __init__(self) -> None:
        self._store: Dict[str, SkillTelemetry] = {}

    def record_usage(self, skill_id: str, success: bool, latency_ms: float) -> None:
        """Records execution telemetry for target skill.

        Args:
            skill_id: Target skill ID string.
            success: Execution success boolean.
            latency_ms: Execution duration in milliseconds.
        """
        if skill_id not in self._store:
            self._store[skill_id] = SkillTelemetry()

        telem = self._store[skill_id]
        telem.execution_count += 1
        if not success:
            telem.failure_count += 1
        telem.avg_latency_ms = (telem.avg_latency_ms + latency_ms) / 2 if telem.execution_count > 1 else latency_ms

    def get_telemetry(self, skill_id: str) -> SkillTelemetry:
        """Retrieves telemetry model for skill_id."""
        return self._store.get(skill_id, SkillTelemetry())
