"""Leader Election selecting a lead coordinator agent for the swarm."""

from typing import List
import structlog

from app.ai.swarm.models import SwarmAgentRecord

logger = structlog.get_logger("leader_election")


class LeaderElection:
    """Dynamically elects a lead coordinator agent based on confidence rating and capability score."""

    async def elect_leader(self, candidates: List[SwarmAgentRecord]) -> SwarmAgentRecord:
        """Elect leader agent."""
        leader = max(candidates, key=lambda a: a.confidence_rating)
        logger.info("Elected swarm leader agent", leader_id=leader.agent_id, name=leader.name)
        return leader
