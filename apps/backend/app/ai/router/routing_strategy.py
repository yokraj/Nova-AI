"""Routing Strategy implements optimization parameters (e.g. quality vs. speed vs. low memory).
"""

from typing import List, Dict, Any
from app.ai.router.models import ModelScore

class RoutingStrategy:
    """Enforces ranking policies depending on system profiles."""

    def __init__(self, mode: str = "LOCAL_FIRST") -> None:
        self.mode = mode # LOCAL_FIRST, QUALITY_FIRST, FASTEST, LOW_MEMORY

    def rank_models(self, models_scores: List[ModelScore]) -> List[ModelScore]:
        """Ranks scores based on the current strategy mode."""
        for score in models_scores:
            # Base final calculation combining metrics
            score.final_score = (
                score.capability_score * 0.5 +
                score.latency_score * 0.3 +
                score.resource_score * 0.2
            )
            
            if self.mode == "FASTEST":
                # Latency weighs more
                score.final_score = score.latency_score * 0.7 + score.capability_score * 0.3
            elif self.mode == "LOW_MEMORY":
                # Resource usage weighs more
                score.final_score = score.resource_score * 0.7 + score.capability_score * 0.3

        # Sort descending by final score
        return sorted(models_scores, key=lambda s: s.final_score, reverse=True)
