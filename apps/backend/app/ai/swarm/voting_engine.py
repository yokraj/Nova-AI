"""Voting Engine supporting majority voting, weighted voting, and confidence scoring."""

from collections import Counter
from typing import Dict, List
import structlog

from app.ai.swarm.models import ConsensusDecision, ConsensusType, VoteRecord, VotingStrategy

logger = structlog.get_logger("voting_engine")


class VotingEngine:
    """Supports majority voting, weighted voting, confidence scoring, and leader decision."""

    def tally_votes(self, votes: List[VoteRecord], strategy: VotingStrategy = VotingStrategy.MAJORITY) -> ConsensusDecision:
        """Tally agent votes and return consensus decision."""
        if not votes:
            return ConsensusDecision(winning_option="default_pass", consensus_type=ConsensusType.FALLBACK)

        if strategy == VotingStrategy.MAJORITY:
            counts = Counter(v.option for v in votes)
            winner, _ = counts.most_common(1)[0]
            breakdown = dict(counts)
            logger.info("Majority vote calculated", winner=winner, breakdown=breakdown)
            return ConsensusDecision(
                winning_option=winner,
                consensus_type=ConsensusType.MAJORITY,
                vote_breakdown=breakdown,
                winning_confidence=1.0,
            )

        elif strategy == VotingStrategy.WEIGHTED or strategy == VotingStrategy.CONFIDENCE:
            scores: Dict[str, float] = {}
            counts: Dict[str, int] = {}
            for v in votes:
                scores[v.option] = scores.get(v.option, 0.0) + v.confidence
                counts[v.option] = counts.get(v.option, 0) + 1
            winner = max(scores, key=scores.get)  # type: ignore
            logger.info("Confidence/Weighted vote calculated", winner=winner, score=scores[winner])
            return ConsensusDecision(
                winning_option=winner,
                consensus_type=ConsensusType.WEIGHTED,
                vote_breakdown=counts,
                winning_confidence=scores[winner],
            )

        else:
            winner = votes[0].option
            return ConsensusDecision(winning_option=winner, consensus_type=ConsensusType.LEADER_OVERRIDE)
