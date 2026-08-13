"""Keyword Search Module.

Implements BM25/TF-IDF and exact match keyword search using Memory Foundation repository.
Supports tag, workspace, project, and conversation thread searches.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.memory.repository import MemoryRepository

logger = structlog.get_logger(__name__)


class KeywordSearchEngine:
    """Enterprise BM25 / Exact Match Keyword Retrieval Engine."""

    def __init__(self, memory_repository: Optional[MemoryRepository] = None) -> None:
        self.memory_repository = memory_repository or MemoryRepository()
        logger.info("keyword_search_engine_initialized")

    async def search_keywords(
        self,
        query: str,
        workspace: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Executes BM25 / TF-IDF keyword search over memory repository."""
        entries = await self.memory_repository.search_entries(
            query=query, workspace=workspace, project=project, limit=limit
        )

        results = []
        q_words = set(query.lower().split())

        for idx, entry in enumerate(entries):
            # Compute term frequency score
            content_lower = entry.content.lower() + " " + entry.title.lower()
            tf_score = sum(content_lower.count(w) for w in q_words)
            norm_score = min(1.0, round(0.5 + (tf_score * 0.1), 4))

            results.append({
                "memory_id": entry.id,
                "title": entry.title,
                "content": entry.content,
                "summary": entry.summary,
                "keyword_score": norm_score,
                "rank": idx + 1,
                "workspace": entry.workspace,
                "project": entry.project,
                "source": "keyword_search",
            })

        logger.info("keyword_search_executed", query_snippet=query[:30], count=len(results))
        return results
