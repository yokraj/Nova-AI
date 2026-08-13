"""Ranking Engine scores retrieved results based on multiple parameters.
"""

from datetime import datetime, timezone
from typing import List
from app.ai.memory.models import RetrievalResult

class RankingEngine:
    """Combines semantic similarity, chronological recency, and priority weights."""

    def rank_results(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """Calculates final scores: Final = Similarity * 0.6 + Importance * 0.2 + Recency * 0.2."""
        now = datetime.now(timezone.utc)
        ranked = []

        for res in results:
            # Parse created_at time from metadata
            created_str = res.metadata.get("created_at")
            if created_str:
                try:
                    created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                except ValueError:
                    created_at = now
            else:
                created_at = now

            importance = float(res.metadata.get("importance_score", 0.5))

            # Calculate recency decay score
            diff_hours = (now - created_at).total_seconds() / 3600.0
            recency = 1.0 / (1.0 + max(0.0, diff_hours))

            # Apply final ranking formula
            final_score = (res.similarity_score * 0.6) + (importance * 0.2) + (recency * 0.2)
            
            res.similarity_score = final_score
            ranked.append(res)

        # Sort descending by updated final score
        return sorted(ranked, key=lambda x: x.similarity_score, reverse=True)
