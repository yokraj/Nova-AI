"""Sync Engine detecting file additions and updates to flag stale documentation.
"""

import hashlib
from typing import List

from app.agents.software_engineer.documentation.interfaces import DocumentationSync
from app.agents.software_engineer.documentation.models import DocumentationChange, SyncResult


class DocumentationSyncEngine(DocumentationSync):
    """Audits workspace files to flag documentation updates requests."""

    def sync_documentation(
        self, workspace_path: str, modified_files: List[str]
    ) -> SyncResult:
        """Determines outdated documents.

        Args:
            workspace_path: Absolute workspace root path.
            modified_files: List of modified file paths.

        Returns:
            SyncResult.
        """
        changes = []
        outdated = []

        for f in modified_files:
            changes.append(
                DocumentationChange(
                    file_path=f,
                    change_type="modified",
                )
            )
            outdated.append(f"{f}.md")

        return SyncResult(outdated_docs=outdated, changes=changes)
