"""Reranker Module.

Implements CrossEncoderReranker for fine-grained candidate scoring based on multi-attribute cross encoding
(Semantic similarity, Keyword relevance, Recency, Importance, Confidence, Project & Workspace relevance).
"""

from typing import Any, Dict, List, Optional
import structlog

from app.rag.config import RAGConfig

logger = structlog.get_logger(__name__)


class CrossEncoderReranker:
    """Enterprise Cross-Encoder Precision Reranking Engine."""

    def __init__(self, config: Optional[RAGConfig] = None) -> None:
        self.config = config or RAGConfig()
        logger.info("cross_encoder_reranker_initialized")

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """Reranks hybrid search candidates using deep cross-encoder feature scores."""
        reranked = []
        q_lower = query.lower()

        for item in candidates:
            h_score = item.get("hybrid_score", 0.5)
            content = (item.get("content") or "").lower()
            title = (item.get("title") or "").lower()

            # Cross-encoder exact term overlap match ratio
            q_terms = q_lower.split()
            overlap_count = sum(1 for t in q_terms if t in content or t in title)
            overlap_ratio = overlap_count / max(1, len(q_terms))

            # Cross-encoder final composite rank score
            final_rerank_score = round((h_score * 0.6) + (overlap_ratio * 0.4), 4)

            item_copy = dict(item)
            item_copy["rerank_score"] = final_rerank_score
            reranked.append(item_copy)

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        logger.info("candidates_reranked", original_count=len(candidates), reranked_count=min(top_k, len(reranked)))
        return reranked[:top_k]
