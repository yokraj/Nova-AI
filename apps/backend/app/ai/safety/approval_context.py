"""Approval Context tracking session metadata and variables.
"""

from typing import Dict, Any

class ApprovalContext:
    """Carries dynamic metadata context variables."""

    def __init__(self, approval_id: str) -> None:
        self.approval_id = approval_id
        self.metadata: Dict[str, Any] = {}

    def set_meta(self, key: str, value: Any) -> None:
        """Sets metadata variables."""
        self.metadata[key] = value

    def get_meta(self, key: str, default: Any = None) -> Any:
        """Retrieves metadata variables."""
        return self.metadata.get(key, default)
