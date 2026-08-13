"""Hybrid Search Module.

Implements Reciprocal Rank Fusion (RRF) and weighted score normalization to merge,
deduplicate, and rank parallel keyword and semantic search candidates.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.rag.config import RAGConfig
from app.rag.keyword_search import KeywordSearchEngine
from app.rag.semantic_search import SemanticSearchEngine

logger = structlog.get_logger(__name__)


class HybridSearchEngine:
    """Enterprise Hybrid Reciprocal Rank Fusion Search Engine."""

    def __init__(
        self,
        config: Optional[RAGConfig] = None,
        keyword_engine: Optional[KeywordSearchEngine] = None,
        semantic_engine: Optional[SemanticSearchEngine] = None,
    ) -> None:
        self.config = config or RAGConfig()
        self.keyword_engine = keyword_engine or KeywordSearchEngine()
        self.semantic_engine = semantic_engine or SemanticSearchEngine()
        logger.info("hybrid_search_engine_initialized")

    async def execute_hybrid_search(
        self,
        query: str,
        workspace: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Executes parallel keyword + semantic retrieval and merges via RRF score fusion."""
        # 1. Parallel Keyword & Semantic Retrieval
        keyword_results = await self.keyword_engine.search_keywords(query, workspace=workspace, project=project, limit=limit)
        semantic_results = await self.semantic_engine.search_semantic(query, workspace=workspace, project=project, limit=limit)

        # 2. Candidate Deduplication Map
        candidate_map: Dict[str, Dict[str, Any]] = {}
        rrf_k = self.config.rrf_k

        # 3. Apply Reciprocal Rank Fusion (RRF)
        for rank, item in enumerate(keyword_results, 1):
            mem_id = item["memory_id"]
            rrf_score = self.config.keyword_weight * (1.0 / (rrf_k + rank))
            if mem_id not in candidate_map:
                candidate_map[mem_id] = dict(item)
                candidate_map[mem_id]["hybrid_score"] = rrf_score
            else:
                candidate_map[mem_id]["hybrid_score"] += rrf_score

        for rank, item in enumerate(semantic_results, 1):
            mem_id = item["memory_id"]
            rrf_score = self.config.semantic_weight * (1.0 / (rrf_k + rank))
            if mem_id not in candidate_map:
                candidate_map[mem_id] = dict(item)
                candidate_map[mem_id]["hybrid_score"] = rrf_score
            else:
                candidate_map[mem_id]["hybrid_score"] += rrf_score
                # Enrich content if missing
                if not candidate_map[mem_id].get("content") and item.get("content"):
                    candidate_map[mem_id]["content"] = item["content"]

        merged = list(candidate_map.values())
        merged.sort(key=lambda x: x["hybrid_score"], reverse=True)

        logger.info(
            "hybrid_search_executed",
            kw_count=len(keyword_results),
            sem_count=len(semantic_results),
            merged_count=len(merged),
        )
        return merged[:limit]
