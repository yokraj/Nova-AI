"""Shared Workflows repository for team workflow publishing and execution.
"""

from typing import Any, Dict, List


class SharedWorkflows:
    """Manages shared workspace workflow repository for team publishing."""

    def __init__(self) -> None:
        self._shared_workflows: List[Dict[str, Any]] = []

    def publish_workflow(self, workspace_id: str, workflow_id: str, title: str) -> Dict[str, Any]:
        """Publishes workflow to team repository."""
        item = {"workspace_id": workspace_id, "workflow_id": workflow_id, "title": title}
        self._shared_workflows.append(item)
        return item
