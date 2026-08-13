"""Approval Queue maintaining active pending gating request queues.
"""

from datetime import datetime
from typing import Dict, List, Optional
from app.ai.safety.models import ApprovalItem

class ApprovalQueue:
    """Manages active, approved, rejected, and expired gating items queues."""

    def __init__(self) -> None:
        self._pending: Dict[str, ApprovalItem] = {}
        self._history: List[ApprovalItem] = []

    def add_pending(self, item: ApprovalItem) -> None:
        """Appends a new pending request to the queue."""
        self._pending[item.approval_id] = item

    def resolve(self, approval_id: str, approved: bool) -> Optional[ApprovalItem]:
        """Resolves request status, moving it to history log files."""
        item = self._pending.pop(approval_id, None)
        if item:
            item.status = "approved" if approved else "rejected"
            item.resolved_at = datetime.utcnow()
            self._history.append(item)
            return item
        return None

    def get_pending(self, approval_id: str) -> Optional[ApprovalItem]:
        """Retrieves a pending request by ID."""
        return self._pending.get(approval_id)

    def list_pending(self) -> List[ApprovalItem]:
        """Lists all pending approval gating requests."""
        return list(self._pending.values())

    def list_history(self) -> List[ApprovalItem]:
        """Lists all completed histories reports."""
        return list(self._history)
