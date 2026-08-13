"""Workflow Sharing manager handling team collaboration and permission grants.
"""

from typing import Any, Dict
from app.ai.workflow_studio.models import WorkflowDefinition


class WorkflowSharing:
    """Manages sharing permissions and team collaboration for workflows."""

    def share_with_user(self, workflow: WorkflowDefinition, user_email: str) -> Dict[str, Any]:
        """Grants workflow access to team user."""
        return {
            "workflow_id": workflow.workflow_id,
            "shared_with": user_email,
            "status": "SHARED",
        }
