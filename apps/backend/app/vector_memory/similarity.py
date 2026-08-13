"""Similarity Engine Module.

Implements vector distance metrics (Cosine similarity, Euclidean distance, Dot product),
Maximum Marginal Relevance (MMR), Top-K candidate extraction, and threshold filtering.
"""

import math
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class SimilarityEngine:
    """Enterprise Mathematical Vector Similarity & MMR Engine."""

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """Calculates cosine similarity between two vectors."""
        if len(v1) != len(v2) or not v1:
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))
        if mag1 == 0.0 or mag2 == 0.0:
            return 0.0
        return round(dot / (mag1 * mag2), 6)

    @staticmethod
    def euclidean_distance(v1: List[float], v2: List[float]) -> float:
        """Calculates Euclidean distance between two vectors."""
        if len(v1) != len(v2):
            return float("inf")
        return round(math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2))), 6)

    @staticmethod
    def dot_product(v1: List[float], v2: List[float]) -> float:
        """Calculates dot product between two vectors."""
        if len(v1) != len(v2):
            return 0.0
        return round(sum(a * b for a, b in zip(v1, v2)), 6)

    @staticmethod
    def filter_by_threshold(candidates: List[Dict[str, Any]], threshold: float) -> List[Dict[str, Any]]:
        """Filters candidate results below threshold score."""
        return [c for c in candidates if c.get("similarity_score", 0.0) >= threshold]

    @staticmethod
    def max_marginal_relevance(
        query_vector: List[float],
        candidates: List[Dict[str, Any]],
        lambda_param: float = 0.5,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Applies Maximum Marginal Relevance (MMR) for diverse, non-redundant vector ranking."""
        if not candidates:
            return []

        selected: List[Dict[str, Any]] = []
        remaining = list(candidates)

        while len(selected) < top_k and remaining:
            best_score = -float("inf")
            best_candidate = None

            for item in remaining:
                cand_vec = item.get("vector", query_vector)
                sim_to_query = SimilarityEngine.cosine_similarity(query_vector, cand_vec)

                # Max similarity to already selected candidates
                max_sim_to_selected = 0.0
                if selected:
                    max_sim_to_selected = max(
                        SimilarityEngine.cosine_similarity(cand_vec, s.get("vector", cand_vec))
                        for s in selected
                    )

                # MMR score formula
                mmr_score = (lambda_param * sim_to_query) - ((1.0 - lambda_param) * max_sim_to_selected)
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_candidate = item

            if best_candidate:
                selected.append(best_candidate)
                remaining.remove(best_candidate)
            else:
                break

        return selected
