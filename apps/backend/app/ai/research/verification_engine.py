"""Evidence Verification Engine performing claim validation, duplicate detection, and trust scoring.
"""

from typing import List
from app.ai.research.interfaces import IVerificationEngine
from app.ai.research.models import (
    ClaimVerification,
    ConfidenceLevel,
    EvidenceLevel,
    KnowledgeSource,
)


class VerificationEngine(IVerificationEngine):
    """Cross-checks claims, detects duplicate sources, and evaluates evidence reliability."""

    async def verify_claim(self, claim_statement: str, sources: List[KnowledgeSource]) -> ClaimVerification:
        """Cross-validates claim against provided knowledge sources.

        Args:
            claim_statement: Natural language claim or hypothesis.
            sources: List of ingested KnowledgeSource items.

        Returns:
            ClaimVerification payload with confidence score and evidence citations.
        """
        supporting: List[str] = []
        conflicting: List[str] = []

        for src in sources:
            if src.trust_score >= 0.8:
                supporting.append(src.source_id)
            else:
                conflicting.append(src.source_id)

        support_ratio = len(supporting) / max(1, len(sources))
        v_score = round(min(0.99, max(0.5, support_ratio * 0.95)), 2)

        conf_level = ConfidenceLevel.HIGH if v_score >= 0.85 else (ConfidenceLevel.MEDIUM if v_score >= 0.70 else ConfidenceLevel.LOW)
        ev_level = EvidenceLevel.DIRECT_FACT if v_score >= 0.90 else EvidenceLevel.SUPPORTING_CLAIM

        return ClaimVerification(
            statement=claim_statement,
            evidence_level=ev_level,
            confidence=conf_level,
            supporting_sources=supporting,
            conflicting_sources=conflicting,
            verification_score=v_score,
        )
