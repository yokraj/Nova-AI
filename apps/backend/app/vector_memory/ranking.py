"""Vector Ranking Module.

Ranks candidates using a weighted composite score of Semantic similarity,
Recency, Importance, Confidence, Workspace relevance, Project relevance, and Popularity.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class VectorRankingEngine:
    """Enterprise Multi-Dimensional Candidate Ranking Engine."""

    def __init__(self, config: Optional[Any] = None) -> None:
        self.config = config
        self.weights = {
            "similarity": 0.45,
            "recency": 0.15,
            "importance": 0.15,
            "confidence": 0.10,
            "workspace_relevance": 0.05,
            "project_relevance": 0.05,
            "popularity": 0.05,
        }
        logger.info("vector_ranking_engine_initialized")

    def rank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        target_workspace: Optional[str] = None,
        target_project: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Calculates multi-attribute composite rank score for candidates."""
        ranked: List[Dict[str, Any]] = []

        for item in candidates:
            sim = item.get("similarity_score", 0.5)
            recency = item.get("recency_score", 0.8)
            importance = item.get("importance", 0.5)
            confidence = item.get("confidence", 1.0)
            popularity = item.get("popularity", 0.2)

            ws_rel = 1.0 if target_workspace and item.get("workspace") == target_workspace else 0.5
            pj_rel = 1.0 if target_project and item.get("project") == target_project else 0.5

            composite_score = (
                (sim * self.weights["similarity"]) +
                (recency * self.weights["recency"]) +
                (importance * self.weights["importance"]) +
                (confidence * self.weights["confidence"]) +
                (ws_rel * self.weights["workspace_relevance"]) +
                (pj_rel * self.weights["project_relevance"]) +
                (popularity * self.weights["popularity"])
            )

            item_copy = dict(item)
            item_copy["composite_rank_score"] = round(composite_score, 4)
            ranked.append(item_copy)

        ranked.sort(key=lambda x: x["composite_rank_score"], reverse=True)
        return ranked
