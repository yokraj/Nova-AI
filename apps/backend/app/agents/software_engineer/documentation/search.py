"""Search Engine querying keyword terms matching indexed document concepts.
"""

from typing import List

from app.agents.software_engineer.documentation.models import KnowledgeIndex, KnowledgeEntry


class LocalDocumentationSearcher:
    """Performs substring text queries over indexed concept fields."""

    def search(self, index: KnowledgeIndex, query: str) -> List[KnowledgeEntry]:
        """Finds matched entries.

        Args:
            index: Indexed database mappings.
            query: User search term.

        Returns:
            List of matching KnowledgeEntry items.
        """
        results = []
        q_lower = query.lower()

        for entry in index.entries.values():
            if q_lower in entry.title.lower() or q_lower in entry.content.lower():
                results.append(entry)

        return results
