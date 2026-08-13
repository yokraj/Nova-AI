"""Semantic Search Module.

Connects to M3.6.2 Vector Engine for Top-K semantic vector search,
MMR diversity ranking, threshold filtering, and workspace/project scoping.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.vector_memory.vector_search import VectorSearch

logger = structlog.get_logger(__name__)


class SemanticSearchEngine:
    """Enterprise Vector Semantic Search Integration Engine."""

    def __init__(self, vector_search: Optional[VectorSearch] = None) -> None:
        self.vector_search = vector_search or VectorSearch()
        logger.info("semantic_search_engine_initialized")

    async def search_semantic(
        self,
        query: str,
        workspace: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 20,
        threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Executes vector semantic search and maps candidates for RAG fusion."""
        vec_results = await self.vector_search.semantic_search(
            query=query, top_k=limit, workspace=workspace, project=project, threshold=threshold
        )

        results = []
        for idx, item in enumerate(vec_results):
            results.append({
                "memory_id": item.memory_id,
                "title": f"Vector Candidate [{item.memory_id[:8]}]",
                "content": item.text_snippet or f"Vector text content snippet for {item.memory_id}",
                "summary": item.text_snippet,
                "semantic_score": item.similarity_score,
                "rank": idx + 1,
                "workspace": item.workspace,
                "project": item.project,
                "source": "semantic_search",
            })

        logger.info("semantic_search_executed", query_snippet=query[:30], count=len(results))
        return results
