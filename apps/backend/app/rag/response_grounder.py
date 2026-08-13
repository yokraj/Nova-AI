"""Response Grounder Module.

Post-processing grounder ensuring final output contains uncertainty warnings or disclaimers
when grounding confidence falls below strict thresholds.
"""

from typing import Any, Dict, Optional
import structlog

from app.rag.grounding import GroundingEngine

logger = structlog.get_logger(__name__)


class ResponseGrounder:
    """Enterprise Output Post-Processing Grounder."""

    def __init__(self, grounding_engine: Optional[GroundingEngine] = None) -> None:
        self.grounding_engine = grounding_engine or GroundingEngine()
        logger.info("response_grounder_initialized")

    def enforce_grounding(self, raw_response: str, context_text: str) -> Dict[str, Any]:
        """Validates raw response against context and appends uncertainty statement if needed."""
        verification = self.grounding_engine.verify_grounding(raw_response, context_text)
        final_text = raw_response

        if verification["uncertainty_required"] and verification["uncertainty_statement"]:
            if verification["uncertainty_statement"] not in final_text:
                final_text += f"\n\n*{verification['uncertainty_statement']}*"

        logger.info("response_grounded", is_grounded=verification["is_grounded"], confidence=verification["confidence_score"])
        return {
            "final_response": final_text,
            "verification": verification,
        }
