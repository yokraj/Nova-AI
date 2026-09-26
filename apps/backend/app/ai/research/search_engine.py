"""Unified Search Engine conducting local, repository, web, and documentation searches.
"""

from typing import Any, List, Optional
from app.ai.research.interfaces import ISearchEngine
from app.ai.research.knowledge_collector import KnowledgeCollector
from app.ai.research.literature_discovery import LiteratureDiscoveryEngine
from app.ai.research.models import KnowledgeSource, SourceType, ScholarlySourceRecord


class SearchEngine(ISearchEngine):
    """Unified search orchestrator handling local docs, repositories, web pages, and APIs."""

    def __init__(self, collector: KnowledgeCollector, lit_discovery: Optional[LiteratureDiscoveryEngine] = None) -> None:
        self.collector = collector
        self.lit_discovery = lit_discovery or LiteratureDiscoveryEngine()

    async def search(self, query: str, **kwargs: Any) -> List[KnowledgeSource]:
        """Searches across configured knowledge providers, scholarly databases, and ranks results.

        Args:
            query: Search inquiry string.
            **kwargs: Filters and source preferences (e.g. use_scholarly=True, title, author, year, doi).

        Returns:
            Ranked list of KnowledgeSource items.
        """
        sources: List[KnowledgeSource] = []

        # 1. Scholarly literature search if requested or query contains research keywords
        use_scholarly = kwargs.get("use_scholarly", True)
        if use_scholarly:
            lit_res = self.lit_discovery.search_literature(
                query=query,
                title=kwargs.get("title"),
                author=kwargs.get("author"),
                year=kwargs.get("year"),
                doi=kwargs.get("doi"),
                limit=kwargs.get("limit", 10),
                selected_providers=kwargs.get("selected_providers"),
            )
            for rec in lit_res.sources:
                sources.append(
                    KnowledgeSource(
                        title=rec.title,
                        url_or_path=rec.canonical_url or rec.source_record_url or f"doi:{rec.doi}",
                        type=SourceType.API,
                        trust_score=0.95 if rec.doi else 0.85,
                        extracted_text=rec.abstract or rec.title,
                        author=", ".join(rec.authors) if rec.authors else None,
                        publication_date=str(rec.publication_year) if rec.publication_year else None,
                    )
                )

        # 2. Fallback to local / documentation knowledge collection if no scholarly sources found
        if not sources:
            local_src = await self.collector.collect_knowledge(f"./docs/{query.replace(' ', '_')}.md")
            sources.append(local_src)

        # Rank sources by trust score
        sources.sort(key=lambda s: s.trust_score, reverse=True)
        return sources

