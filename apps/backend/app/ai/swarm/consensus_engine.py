"""Consensus Engine orchestrating agent voting and reaching swarm consensus."""

from typing import List, Optional
import structlog

from app.ai.swarm.interfaces import IConsensusEngine
from app.ai.swarm.models import ConsensusDecision, VoteRecord, VotingStrategy
from app.ai.swarm.voting_engine import VotingEngine

logger = structlog.get_logger("consensus_engine")


class ConsensusEngine(IConsensusEngine):
    """Aggregates votes and reaches consensus across agents using configured voting strategies."""

    def __init__(self, voting_engine: Optional[VotingEngine] = None) -> None:
        self.voting = voting_engine or VotingEngine()

    async def reach_consensus(self, votes: List[VoteRecord], strategy: str = "majority") -> ConsensusDecision:
        """Reach consensus across votes."""
        strat = VotingStrategy(strategy) if strategy in [s.value for s in VotingStrategy] else VotingStrategy.MAJORITY
        decision = self.voting.tally_votes(votes, strategy=strat)
        logger.info("Reached swarm consensus", decision=decision.winning_option, type=decision.consensus_type.value)
        return decision
