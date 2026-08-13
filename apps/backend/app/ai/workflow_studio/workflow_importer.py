"""Workflow Importer importing workflow definitions from JSON/YAML file content.
"""

import json
from app.ai.workflow_studio.models import WorkflowDefinition


class WorkflowImporter:
    """Imports JSON or YAML string content into WorkflowDefinition objects."""

    def import_from_json(self, content: str) -> WorkflowDefinition:
        """Imports WorkflowDefinition from JSON content.

        Args:
            content: JSON string content.

        Returns:
            WorkflowDefinition instance.
        """
        data = json.loads(content)
        return WorkflowDefinition.model_validate(data)
