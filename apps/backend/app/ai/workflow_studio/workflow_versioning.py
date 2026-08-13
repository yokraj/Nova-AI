"""Workflow Versioning manager handling semantic version history and revisions.
"""

from typing import List
from app.ai.workflow_studio.models import WorkflowDefinition


class WorkflowVersioning:
    """Manages semantic version history and rollback revisions for workflows."""

    def increment_version(self, workflow: WorkflowDefinition, bump_type: str = "patch") -> WorkflowDefinition:
        """Increments semantic version string (1.0.0 -> 1.0.1)."""
        parts = [int(p) for p in workflow.version.split(".")]
        if bump_type == "minor":
            parts[1] += 1
            parts[2] = 0
        else:
            parts[2] += 1
        workflow.version = f"{parts[0]}.{parts[1]}.{parts[2]}"
        return workflow
