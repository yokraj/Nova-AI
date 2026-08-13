"""Workspace Import importing workspace definitions from encrypted package archives.
"""

import json
from app.ai.workspace.models import WorkspaceDefinition


class WorkspaceImport:
    """Imports encrypted workspace archives into WorkspaceDefinition instances."""

    def import_workspace_package(self, content: str) -> WorkspaceDefinition:
        """Imports WorkspaceDefinition from JSON content."""
        data = json.loads(content)
        return WorkspaceDefinition.model_validate(data)
