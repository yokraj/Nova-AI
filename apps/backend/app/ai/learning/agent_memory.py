"""Agent Memory — maintains per-agent accumulated knowledge and cross-agent sharing."""

import structlog
from datetime import datetime
from typing import Dict, List, Optional

from app.ai.learning.configuration import LearningConfiguration
from app.ai.learning.experience_store import ExperienceStore
from app.ai.learning.exceptions import AgentExperienceError
from app.ai.learning.models import AgentExperience, ExperienceOutcome

logger = structlog.get_logger("agent_memory")


class AgentMemory:
    """Maintains per-agent learning records and facilitates cross-agent knowledge sharing.

    Each agent accumulates:
    - Mission history (total, successful)
    - Domain expertise scores updated after each experience
    - Preferred strategy references
    - Improvement suggestions from the learning engine

    Cross-agent sharing is enabled by copying high-performing agents'
    preferred strategies and domain expertise to newly-observed agents.
    """

    def __init__(
        self,
        store: Optional[ExperienceStore] = None,
        config: Optional[LearningConfiguration] = None,
    ) -> None:
        self.store = store or ExperienceStore()
        self.config = config or LearningConfiguration()
        self._records: Dict[str, AgentExperience] = {}

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def update_from_experience_store(self) -> None:
        """Rebuild all agent records by scanning the full experience store."""
        for experience in self.store.list_experiences():
            for agent_id in experience.agents_used:
                self._update_agent(agent_id, experience)

    def record_experience(
        self, agent_id: str, experience_outcome: str, goal: str, duration: float
    ) -> None:
        """Record a single experience outcome for a specific agent."""
        from app.ai.learning.models import ExperienceOutcome

        record = self._get_or_create(agent_id)
        record.total_missions += 1

        if experience_outcome in (
            ExperienceOutcome.COMPLETED.value, "success", "completed"
        ):
            record.successful_missions += 1

        # Update success rate
        record.success_rate = round(
            record.successful_missions / record.total_missions, 4
        )
        record.last_updated = datetime.utcnow()

        # Update domain expertise based on goal keywords
        keyword = goal.split()[0].lower() if goal else "generic"
        current = record.domain_expertise.get(keyword, 0.0)
        record.domain_expertise[keyword] = round(min(1.0, current + 0.05), 4)

        self._records[agent_id] = record

    def assign_strategy(self, agent_id: str, strategy_id: str) -> None:
        """Assign a preferred strategy to an agent."""
        record = self._get_or_create(agent_id)
        if strategy_id not in record.preferred_strategies:
            record.preferred_strategies.append(strategy_id)
        self._records[agent_id] = record

    def add_suggestion(self, agent_id: str, suggestion: str) -> None:
        """Append an improvement suggestion for an agent."""
        record = self._get_or_create(agent_id)
        if suggestion not in record.improvement_suggestions:
            record.improvement_suggestions.append(suggestion)
        self._records[agent_id] = record

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_experience(self, agent_id: str) -> Optional[AgentExperience]:
        """Return the accumulated experience record for a given agent."""
        return self._records.get(agent_id)

    def list_agents(self) -> List[str]:
        """Return all known agent IDs."""
        return list(self._records.keys())

    def top_agents(self, limit: int = 5) -> List[AgentExperience]:
        """Return the top-performing agents by success rate."""
        ranked = sorted(
            self._records.values(),
            key=lambda a: (a.success_rate, a.total_missions),
            reverse=True,
        )
        return ranked[:limit]

    def average_learning_score(self) -> float:
        """Compute the average agent learning score (success_rate × experience depth)."""
        records = list(self._records.values())
        if not records:
            return 0.0
        scores = [
            r.success_rate * min(1.0, r.total_missions / 10)
            for r in records
        ]
        return round(sum(scores) / len(scores), 4)

    # ------------------------------------------------------------------
    # Cross-Agent Sharing
    # ------------------------------------------------------------------

    def share_strategies_to(self, target_agent_id: str) -> None:
        """Copy top-performing agents' preferred strategies to a target agent.

        Only propagates strategies when cross-agent sharing is enabled and
        the target agent has a lower success rate than the top performers.
        """
        if not self.config.enable_cross_agent_sharing:
            return

        target = self._get_or_create(target_agent_id)
        top = self.top_agents(limit=3)

        for donor in top:
            if donor.agent_id == target_agent_id:
                continue
            if donor.success_rate > target.success_rate:
                for sid in donor.preferred_strategies:
                    if sid not in target.preferred_strategies:
                        target.preferred_strategies.append(sid)
                        logger.info(
                            "Cross-agent strategy shared",
                            from_agent=donor.agent_id,
                            to_agent=target_agent_id,
                            strategy_id=sid,
                        )

        self._records[target_agent_id] = target

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _get_or_create(self, agent_id: str) -> AgentExperience:
        if agent_id not in self._records:
            self._records[agent_id] = AgentExperience(agent_id=agent_id)
        return self._records[agent_id]

    def _update_agent(self, agent_id: str, experience: Any) -> None:
        """Update agent record from an experience object (used in bulk rebuild)."""
        record = self._get_or_create(agent_id)
        record.total_missions += 1

        if experience.outcome == ExperienceOutcome.COMPLETED:
            record.successful_missions += 1

        if record.total_missions > 0:
            record.success_rate = round(
                record.successful_missions / record.total_missions, 4
            )

        keyword = self._dominant_keyword(experience.goal)
        current = record.domain_expertise.get(keyword, 0.0)
        record.domain_expertise[keyword] = round(min(1.0, current + 0.05), 4)
        record.last_updated = datetime.utcnow()
        self._records[agent_id] = record

    @staticmethod
    def _dominant_keyword(goal: str) -> str:
        stop = {"a", "an", "the", "and", "or", "to", "of", "in", "for", "with"}
        words = [w.lower().strip(".,;:!?") for w in goal.split() if len(w) > 2]
        filtered = [w for w in words if w not in stop]
        return filtered[0] if filtered else "generic"


# Type alias for internal usage avoiding circular import
from typing import Any  # noqa: E402 (placed at module bottom intentionally)
