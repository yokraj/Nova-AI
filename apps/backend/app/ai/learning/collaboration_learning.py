"""Collaboration Learning — orchestrates cross-agent experience sharing."""

import structlog
from typing import Dict, Any, List, Optional

from app.ai.learning.agent_memory import AgentMemory
from app.ai.learning.configuration import LearningConfiguration
from app.ai.learning.experience_store import ExperienceStore
from app.ai.learning.models import ExperienceOutcome

logger = structlog.get_logger("collaboration_learning")


class CollaborationLearning:
    """Enables teams of agents to learn from one another's experiences.

    Responsibilities:
    - Aggregate team success rates across recent experiences
    - Propagate high-performing strategies from top agents to newcomers
    - Surface collective improvement suggestions for collaboration patterns
    """

    def __init__(
        self,
        store: Optional[ExperienceStore] = None,
        agent_memory: Optional[AgentMemory] = None,
        config: Optional[LearningConfiguration] = None,
    ) -> None:
        self.store = store or ExperienceStore()
        self.agent_memory = agent_memory or AgentMemory(store=self.store)
        self.config = config or LearningConfiguration()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def sync_team_knowledge(self, agent_ids: List[str]) -> Dict[str, Any]:
        """Propagate cross-agent strategy sharing for all agents in a team.

        Args:
            agent_ids: List of agent identifiers participating in a mission.

        Returns:
            A summary dict with sharing statistics.
        """
        if not self.config.enable_cross_agent_sharing or not agent_ids:
            return {"shared": False, "reason": "cross_agent_sharing_disabled"}

        shared_count = 0
        for agent_id in agent_ids:
            before = len(
                (self.agent_memory.get_experience(agent_id) or _empty()).preferred_strategies
            )
            self.agent_memory.share_strategies_to(agent_id)
            after = len(
                (self.agent_memory.get_experience(agent_id) or _empty()).preferred_strategies
            )
            shared_count += max(0, after - before)

        logger.info(
            "Team knowledge sync complete",
            agents=len(agent_ids),
            new_strategy_propagations=shared_count,
        )
        return {
            "shared": True,
            "agents_synced": len(agent_ids),
            "new_strategy_propagations": shared_count,
        }

    def team_success_rate(self, agent_ids: List[str]) -> float:
        """Compute the average success rate across a set of agents."""
        rates = []
        for agent_id in agent_ids:
            record = self.agent_memory.get_experience(agent_id)
            if record:
                rates.append(record.success_rate)
        return round(sum(rates) / len(rates), 4) if rates else 0.0

    def top_team(self, agent_ids: List[str], size: int = 3) -> List[str]:
        """Select the top *size* agents from the given list by success rate."""
        scored: List[tuple] = []
        for agent_id in agent_ids:
            record = self.agent_memory.get_experience(agent_id)
            rate = record.success_rate if record else 0.0
            scored.append((agent_id, rate))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [agent_id for agent_id, _ in scored[:size]]

    def generate_collaboration_suggestions(
        self, agent_ids: List[str]
    ) -> List[str]:
        """Generate human-readable improvement suggestions for a team."""
        suggestions: List[str] = []
        rate = self.team_success_rate(agent_ids)

        if rate < 0.5:
            suggestions.append(
                "Consider reducing team size — current configuration shows low success rate."
            )
        if len(agent_ids) > 5:
            suggestions.append(
                "Large agent teams tend to produce coordination overhead. "
                "Prefer focused 2–3 agent groups."
            )
        if rate >= 0.85:
            suggestions.append(
                "Team configuration is highly effective. "
                "Consider promoting this arrangement as a preferred pattern."
            )

        return suggestions

    def export_team_summary(self, agent_ids: List[str]) -> Dict[str, Any]:
        """Return a structured summary of team-level learning metrics."""
        return {
            "team_size": len(agent_ids),
            "team_success_rate": self.team_success_rate(agent_ids),
            "top_agents": self.top_team(agent_ids),
            "suggestions": self.generate_collaboration_suggestions(agent_ids),
        }


def _empty():
    """Return a dummy AgentExperience with empty preferred_strategies."""
    from app.ai.learning.models import AgentExperience
    return AgentExperience(agent_id="__empty__")
