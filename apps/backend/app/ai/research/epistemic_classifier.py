"""Epistemic Classifier for Phase 10L-C: Evidence-Grounded Research Answer Synthesis.

Distinguishes verified facts, derived inferences, and unsupported claims, quantifies confidence,
and prevents unsupported claims from masquerading as verified facts.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
import structlog

from app.ai.research.citation_mapper import ClaimCitationMapper
from app.ai.research.evidence_graph_builder import (
    HEDGING_MARKERS,
    EvidenceGraphBuilder,
)
from app.ai.research.models import (
    ClaimEpistemicStatus,
    ClaimVerificationOutcome,
    ConfidenceLevel,
    GroundedClaim,
)

logger = structlog.get_logger("epistemic_classifier")


class EpistemicClassifier:
    """Evaluates and classifies propositions into verified facts, hedged inferences, or unsupported claims."""

    def __init__(self, citation_mapper: Optional[ClaimCitationMapper] = None) -> None:
        self.citation_mapper = citation_mapper or ClaimCitationMapper()

    def _detect_hedging(self, text: str) -> Tuple[bool, Optional[str]]:
        """Checks if text contains hedging markers indicating derived inference or uncertainty."""
        text_lower = text.lower()
        for marker in HEDGING_MARKERS:
            if marker in text_lower:
                return True, f"Statement uses explicit epistemic hedging: '{marker}'"

        inference_indicators = ["likely", "probable", "might", "potentially", "extrapolated", "theorized", "inferred"]
        for ind in inference_indicators:
            if re.search(rf"\b{ind}\b", text_lower):
                return True, f"Statement contains probabilistic inference marker: '{ind}'"

        return False, None

    def evaluate_statement(
        self,
        statement: str,
        evidence_builder: EvidenceGraphBuilder,
    ) -> GroundedClaim:
        """Evaluates a single natural language claim against the evidence graph.

        Strictly enforces epistemic boundaries:
        - SUPPORTED + unhedged -> VERIFIED_FACT
        - SUPPORTED + hedged -> INFERENCE
        - INSUFFICIENT_EVIDENCE / UNVERIFIED_ASSUMPTION -> UNSUPPORTED
        - CONTRADICTED -> CONTRADICTED (placed in unsupported/contradicted category)
        """
        clean_stmt = re.sub(r"\s+", " ", statement).strip()
        is_hedged, hedge_reason = self._detect_hedging(clean_stmt)

        # Query EvidenceGraphBuilder from Phase 10L-B
        verification_detail = evidence_builder.verify_claim(clean_stmt)
        outcome = verification_detail.outcome
        num_sources = verification_detail.independent_sources_count
        supporting_passages = verification_detail.supporting_passages
        contradicting_passages = verification_detail.contradicting_passages

        # Map citation keys
        citation_keys = self.citation_mapper.get_citation_keys_for_passages(
            supporting_passages,
            evidence_builder,
        )

        # Classification logic
        if outcome == ClaimVerificationOutcome.SUPPORTED:
            if is_hedged:
                epistemic_status = ClaimEpistemicStatus.INFERENCE
                confidence = ConfidenceLevel.MEDIUM if num_sources >= 1 else ConfidenceLevel.LOW
                score = 0.75 if num_sources >= 2 else 0.65
            else:
                epistemic_status = ClaimEpistemicStatus.VERIFIED_FACT
                if num_sources >= 2:
                    confidence = ConfidenceLevel.HIGH
                    score = 0.95
                else:
                    confidence = ConfidenceLevel.HIGH if verification_detail.supporting_passages else ConfidenceLevel.MEDIUM
                    score = 0.90 if verification_detail.supporting_passages else 0.80

        elif outcome == ClaimVerificationOutcome.CONTRADICTED:
            epistemic_status = ClaimEpistemicStatus.CONTRADICTED
            confidence = ConfidenceLevel.LOW
            score = 0.15

        elif outcome == ClaimVerificationOutcome.INSUFFICIENT_EVIDENCE:
            epistemic_status = ClaimEpistemicStatus.UNSUPPORTED
            confidence = ConfidenceLevel.UNVERIFIED
            score = 0.20

        else:  # UNVERIFIED_ASSUMPTION or orphan
            epistemic_status = ClaimEpistemicStatus.UNSUPPORTED
            confidence = ConfidenceLevel.UNVERIFIED
            score = 0.05

        return GroundedClaim(
            statement=clean_stmt,
            epistemic_status=epistemic_status,
            confidence=confidence,
            confidence_score=score,
            supporting_passages=supporting_passages,
            contradicting_passages=contradicting_passages,
            citation_keys=citation_keys,
            is_hedged=is_hedged,
            hedging_rationale=hedge_reason,
            independent_sources_count=num_sources,
        )

    def classify_statements(
        self,
        statements: List[str],
        evidence_builder: EvidenceGraphBuilder,
    ) -> Tuple[List[GroundedClaim], List[GroundedClaim], List[GroundedClaim]]:
        """Separates statements into (verified_facts, derived_inferences, unsupported_claims).

        Guarantees that unsupported or contradicted claims NEVER appear in verified_facts!
        """
        verified_facts: List[GroundedClaim] = []
        derived_inferences: List[GroundedClaim] = []
        unsupported_claims: List[GroundedClaim] = []

        for stmt in statements:
            if not stmt or not stmt.strip():
                continue
            grounded = self.evaluate_statement(stmt, evidence_builder)

            if grounded.epistemic_status == ClaimEpistemicStatus.VERIFIED_FACT:
                verified_facts.append(grounded)
            elif grounded.epistemic_status == ClaimEpistemicStatus.INFERENCE:
                derived_inferences.append(grounded)
            else:
                # Both UNSUPPORTED and CONTRADICTED go to unsupported/unverified category
                unsupported_claims.append(grounded)

        return verified_facts, derived_inferences, unsupported_claims

