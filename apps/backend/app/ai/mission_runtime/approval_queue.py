"""Approval Queue managing sensitive action prompts, human approval holds, and state transitions.
"""

from typing import Any, Dict, List, Optional
from app.ai.mission_runtime.interfaces import IApprovalQueue
from app.ai.mission_runtime.models import ApprovalItem


class ApprovalQueue(IApprovalQueue):
    """Approval Queue managing human-in-the-loop permission requests."""

    def __init__(self) -> None:
        self._items: Dict[str, ApprovalItem] = {}

    async def request_approval(self, mission_id: str, action: str, details: str) -> ApprovalItem:
        """Enqueues a sensitive action requiring explicit user permission.

        Args:
            mission_id: Parent mission ID string.
            action: Action title (e.g., Transfer Money).
            details: Details prompt (e.g., ₹10,000 to Account XXX).

        Returns:
            ApprovalItem model instance.
        """
        item = ApprovalItem(
            mission_id=mission_id,
            action_title=action,
            amount_or_details=details,
            status="pending",
        )
        self._items[item.approval_id] = item
        return item

    async def approve(self, approval_id: str) -> ApprovalItem:
        """Approves a pending approval request.

        Args:
            approval_id: Target approval ID string.

        Returns:
            ApprovalItem updated model.
        """
        item = self._items.get(approval_id)
        if item:
            item.status = "approved"
            return item
        raise ValueError(f"Approval ID '{approval_id}' not found.")

    async def reject(self, approval_id: str, reason: str = "") -> ApprovalItem:
        """Rejects a pending approval request."""
        item = self._items.get(approval_id)
        if item:
            item.status = "rejected"
            item.reason = reason
            return item
        raise ValueError(f"Approval ID '{approval_id}' not found.")

    async def list_pending_approvals(self) -> List[ApprovalItem]:
        """Returns all items awaiting user decision."""
        return [i for i in self._items.values() if i.status == "pending"]
