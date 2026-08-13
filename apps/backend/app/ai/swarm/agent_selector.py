"""Agent Selector selecting optimal candidate agent based on workload and confidence."""

from typing import List, Optional
import structlog

from app.ai.swarm.models import SwarmAgentRecord, SwarmTask

logger = structlog.get_logger("agent_selector")


class AgentSelector:
    """Selects best candidate agent based on idle status and confidence rating."""

    def select_best_agent(self, candidates: List[SwarmAgentRecord]) -> SwarmAgentRecord:
        """Select best candidate."""
        idle_candidates = [c for c in candidates if not c.is_busy]
        pool = idle_candidates if idle_candidates else candidates
        best = max(pool, key=lambda c: c.confidence_rating)
        logger.debug("Selected best agent", agent_id=best.agent_id, name=best.name)
        return best
