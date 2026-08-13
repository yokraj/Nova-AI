"""Conflict Resolver detecting conflicting task outputs and invoking consensus voting."""

from typing import List, Optional
import structlog

from app.ai.swarm.consensus_engine import ConsensusEngine
from app.ai.swarm.models import ConsensusDecision, VoteRecord

logger = structlog.get_logger("conflict_resolver")


class ConflictResolver:
    """Detects conflicting task outputs and resolves disagreements via consensus voting."""

    def __init__(self, consensus_engine: Optional[ConsensusEngine] = None) -> None:
        self.consensus = consensus_engine or ConsensusEngine()

    async def resolve_conflict(self, task_id: str, votes: List[VoteRecord]) -> ConsensusDecision:
        """Resolve conflicting outputs for a task."""
        logger.info("Resolving task conflict via consensus voting", task_id=task_id, votes_count=len(votes))
        decision = await self.consensus.reach_consensus(votes, strategy="majority")
        return decision
