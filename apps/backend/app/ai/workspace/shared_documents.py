"""Shared Documents manager for team specifications, markdown docs, and whitepapers.
"""

from typing import Any, Dict, List


class SharedDocuments:
    """Manages shared team markdown specifications, technical documentation, and whitepapers."""

    def list_documents(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Returns list of shared workspace document specs."""
        return [
            {"doc_id": "doc_arch_001", "title": "Enterprise System Architecture Spec", "author": "lead@corp.org"},
        ]
