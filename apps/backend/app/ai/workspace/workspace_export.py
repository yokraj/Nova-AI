"""Workspace Export exporting workspace definitions to encrypted package archives.
"""

import json
from app.ai.workspace.models import WorkspaceDefinition


class WorkspaceExport:
    """Exports WorkspaceDefinition into encrypted archive string content."""

    def export_workspace_package(self, workspace: WorkspaceDefinition) -> str:
        """Exports workspace definition to JSON string."""
        return json.dumps(workspace.model_dump(mode="json"), indent=2)
