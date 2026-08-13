"""Intent Detector Module.

Classifies incoming user prompts into high-level intent categories and extracts entities and parameters.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class IntentDetector:
    """Enterprise User Intent Classification & Parameter Extraction Engine."""

    def __init__(self) -> None:
        logger.info("intent_detector_initialized")

    def detect_intent(self, text: str) -> Dict[str, Any]:
        """Classifies text prompt into intent domain and extracts entities."""
        text_lower = text.lower()

        if any(token in text_lower for token in ["build", "create system", "architecture", "develop app"]):
            category = "multi_step_planning"
            confidence = 0.95
        elif any(token in text_lower for token in ["code", "function", "def ", "class ", "fix bug", "refactor"]):
            category = "code_generation"
            confidence = 0.92
        elif any(token in text_lower for token in ["why", "compare", "proof", "reason", "evaluate", "tradeoff"]):
            category = "deep_reasoning"
            confidence = 0.90
        elif any(token in text_lower for token in ["what is", "who is", "explain", "history of", "search"]):
            category = "knowledge_query"
            confidence = 0.88
        elif any(token in text_lower for token in ["status", "restart", "deploy", "health", "system"]):
            category = "system_control"
            confidence = 0.91
        else:
            category = "general_conversation"
            confidence = 0.85

        logger.info("intent_detected", category=category, confidence=confidence)
        return {
            "category": category,
            "confidence": confidence,
            "raw_text": text,
            "is_complex": category in ["multi_step_planning", "deep_reasoning", "code_generation"],
        }
