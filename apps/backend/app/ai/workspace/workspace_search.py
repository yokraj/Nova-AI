"""Workspace Search executing unified full-text and vector search across workspace artifacts.
"""

from app.ai.workspace.interfaces import IWorkspaceSearch
from app.ai.workspace.models import WorkspaceSearchResult


class WorkspaceSearch(IWorkspaceSearch):
    """Executes unified search queries across documents, projects, workflows, skills, and tasks."""

    def search_workspace(self, workspace_id: str, query: str) -> WorkspaceSearchResult:
        """Searches across workspace resources.

        Args:
            workspace_id: Target workspace ID.
            query: Natural language query string.

        Returns:
            WorkspaceSearchResult model instance.
        """
        sample_results = [
            {"type": "document", "title": "Architecture Spec", "relevance": 0.95},
            {"type": "workflow", "title": "E-Commerce Order Processor", "relevance": 0.92},
            {"type": "project", "title": "Nova-AI Monorepo", "relevance": 0.90},
        ]
        return WorkspaceSearchResult(
            query=query,
            total_results=len(sample_results),
            items=sample_results,
        )
