"""Approval History logger saving copies of resolved gating items.
"""

from typing import List
from app.ai.safety.models import ApprovalItem

class ApprovalHistory:
    """Stores a log of resolved approval items."""

    def __init__(self) -> None:
        self.history: List[ApprovalItem] = []

    def log_resolved(self, item: ApprovalItem) -> None:
        """Appends resolved item snapshot."""
        self.history.append(item.model_copy())
