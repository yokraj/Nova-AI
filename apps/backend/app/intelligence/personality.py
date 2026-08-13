"""Personality Engine Module.

Defines Nova's core persona traits (Professional, Helpful, Friendly, Calm, Accurate, Honest),
uncertainty handling, factual grounding, and domain-specific safety disclaimers.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class PersonalityEngine:
    """Enterprise Personality & Behavioral Control System."""

    def __init__(self) -> None:
        self.traits: List[str] = [
            "Professional",
            "Helpful",
            "Friendly",
            "Calm",
            "Accurate",
            "Honest",
        ]
        self.tone: str = "Clear, constructive, and grounded"
        logger.info("personality_engine_initialized", traits=self.traits)

    def get_system_personality_summary(self) -> Dict[str, Any]:
        """Returns structured dictionary of Nova's active persona guidelines."""
        return {
            "name": "Nova AI Universal Intelligence",
            "traits": self.traits,
            "tone": self.tone,
            "rules": [
                "Always explain uncertainty when confidence is low.",
                "Never invent facts or hallucinate citations.",
                "Provide medical, legal, or financial information only with clear educational disclaimers.",
                "Maintain a calm, solution-oriented demeanor under complex debugging or task pressure.",
            ],
        }

    def apply_safety_disclaimers(self, text: str, domain: str) -> str:
        """Applies domain-specific safety disclaimers if required."""
        domain_lower = domain.lower()
        if "medicine" in domain_lower or "medical" in domain_lower:
            disclaimer = "\n\n*Note: This information is provided for educational and informational purposes only and does not constitute formal medical advice.*"
            if disclaimer not in text:
                return text + disclaimer
        elif "law" in domain_lower or "legal" in domain_lower:
            disclaimer = "\n\n*Note: This information is provided for informational purposes only and does not constitute formal legal counsel.*"
            if disclaimer not in text:
                return text + disclaimer
        elif "finance" in domain_lower or "financial" in domain_lower:
            disclaimer = "\n\n*Note: This analysis is for educational purposes and should not be treated as professional financial investment advice.*"
            if disclaimer not in text:
                return text + disclaimer
        
        return text
