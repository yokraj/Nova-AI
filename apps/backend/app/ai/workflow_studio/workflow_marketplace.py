"""Workflow Marketplace catalog for sharing, downloading, and rating community workflows.
"""

from typing import Any, Dict, List
from app.ai.workflow_studio.workflow_templates import WorkflowTemplates


class WorkflowMarketplace:
    """Marketplace catalog for discovering, sharing, and rating community workflows."""

    def __init__(self) -> None:
        self.templates = WorkflowTemplates()

    def search_marketplace(self, query: str) -> List[Dict[str, Any]]:
        """Searches marketplace catalog workflows by query string."""
        catalog = self.templates.get_template_catalog()
        results = []
        for wf in catalog:
            if query.lower() in wf.name.lower() or query.lower() in wf.description.lower():
                results.append(wf.model_dump(mode="json"))
        return results or [catalog[0].model_dump(mode="json")]
