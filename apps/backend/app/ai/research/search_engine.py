"""Unified Search Engine conducting local, repository, web, and documentation searches.
"""

from typing import Any, List
from app.ai.research.interfaces import ISearchEngine
from app.ai.research.knowledge_collector import KnowledgeCollector
from app.ai.research.models import KnowledgeSource, SourceType


class SearchEngine(ISearchEngine):
    """Unified search orchestrator handling local docs, repositories, web pages, and APIs."""

    def __init__(self, collector: KnowledgeCollector) -> None:
        self.collector = collector

    async def search(self, query: str, **kwargs: Any) -> List[KnowledgeSource]:
        """Searches across configured knowledge providers and ranks results.

        Args:
            query: Search inquiry string.
            **kwargs: Filters and source preferences.

        Returns:
            Ranked list of KnowledgeSource items.
        """
        sources: List[KnowledgeSource] = []

        # Local document search
        local_src = await self.collector.collect_knowledge(f"./docs/{query.replace(' ', '_')}.md")
        sources.append(local_src)

        # Repository search
        repo_src = await self.collector.collect_knowledge(f"repo://codebase/{query.replace(' ', '_')}")
        sources.append(repo_src)

        # Web & documentation search
        web_src = await self.collector.collect_knowledge(f"https://docs.nova.ai/search?q={query}")
        sources.append(web_src)

        # Rank sources by trust score
        sources.sort(key=lambda s: s.trust_score, reverse=True)
        return sources
