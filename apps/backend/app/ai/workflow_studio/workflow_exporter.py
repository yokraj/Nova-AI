"""Workflow Exporter exporting workflow definitions to JSON and YAML formats.
"""

import json
from app.ai.workflow_studio.models import WorkflowDefinition


class WorkflowExporter:
    """Exports WorkflowDefinition objects into serialized JSON or YAML strings."""

    def export_to_json(self, workflow: WorkflowDefinition) -> str:
        """Exports workflow definition to JSON string.

        Args:
            workflow: Target WorkflowDefinition instance.

        Returns:
            JSON string representation.
        """
        return json.dumps(workflow.model_dump(mode="json"), indent=2)
