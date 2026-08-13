"""Knowledge Index managing searchable indexes maps.
"""

from typing import List

from app.agents.software_engineer.documentation.interfaces import KnowledgeIndexer
from app.agents.software_engineer.documentation.models import KnowledgeEntry, KnowledgeIndex


class LocalKnowledgeIndexer(KnowledgeIndexer):
    """Indexes concepts into local mapping indexes."""

    def index_knowledge(
        self, entries: List[KnowledgeEntry]
    ) -> KnowledgeIndex:
        """Indexes concepts.

        Args:
            entries: List of knowledge entries.

        Returns:
            KnowledgeIndex.
        """
        mapping = {}
        for entry in entries:
            key = entry.title.lower().replace(" ", "_")
            mapping[key] = entry

        return KnowledgeIndex(entries=mapping)
