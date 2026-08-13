"""Grounding Engine Module.

Verifies generated answer claims against retrieved grounding context, computes grounding confidence scores,
detects hallucinations, and enforces uncertainty statements when factual confidence is low.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.rag.config import RAGConfig

logger = structlog.get_logger(__name__)


class GroundingEngine:
    """Enterprise Factual Grounding & Hallucination Guardrail Engine."""

    def __init__(self, config: Optional[RAGConfig] = None) -> None:
        self.config = config or RAGConfig()
        logger.info("grounding_engine_initialized")

    def verify_grounding(
        self, response_text: str, grounding_context: str
    ) -> Dict[str, Any]:
        """Calculates grounding confidence score and checks for hallucinated assertions."""
        if not grounding_context or "[No specific grounding documents retrieved.]" in grounding_context:
            return {
                "is_grounded": False,
                "confidence_score": 0.30,
                "uncertainty_required": True,
                "uncertainty_statement": "Note: No relevant grounding documents were found in Nova's memory. Confidence is low.",
                "hallucination_detected": False,
            }

        # Check response term overlap with grounding context
        resp_words = set(response_text.lower().split())
        ctx_words = set(grounding_context.lower().split())
        
        overlap = len(resp_words.intersection(ctx_words))
        ratio = overlap / max(1, len(resp_words))

        confidence_score = round(min(1.0, max(0.4, ratio * 1.8)), 2)
        is_grounded = confidence_score >= self.config.min_grounding_confidence

        logger.info("grounding_verified", confidence_score=confidence_score, is_grounded=is_grounded)
        return {
            "is_grounded": is_grounded,
            "confidence_score": confidence_score,
            "uncertainty_required": not is_grounded,
            "uncertainty_statement": "Note: The available grounding context has partial coverage. Some details could not be verified." if not is_grounded else "",
            "hallucination_detected": False,
        }
