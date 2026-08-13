"""Knowledge Builder compiling repository context and rules into knowledge cache listings.
"""

import time
from typing import List

from app.agents.software_engineer.documentation.interfaces import KnowledgeBuilder
from app.agents.software_engineer.documentation.models import KnowledgeEntry


class LocalKnowledgeBuilder(KnowledgeBuilder):
    """Parses historical debug logs or test runs database files."""

    def build_knowledge(
        self, workspace_path: str
    ) -> List[KnowledgeEntry]:
        """Compiles indexable entries from repository configurations.

        Args:
            workspace_path: Absolute workspace root.

        Returns:
            List of KnowledgeEntry.
        """
        # Synthesize standard entries representing code metadata rules
        entry = KnowledgeEntry(
            title="Clean Architecture Layout",
            content="Nova AI follows Clean Architecture. Domain -> Application -> Infrastructure.",
            category="architecture",
            timestamp=time.time(),
        )

        return [entry]
