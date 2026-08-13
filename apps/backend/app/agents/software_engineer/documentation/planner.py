"""Documentation Planner decomposing documentation tasks checklists.
"""

import time
from app.agents.software_engineer.documentation.interfaces import DocumentationPlanner
from app.agents.software_engineer.documentation.models import (
    DocumentationContext,
    DocumentationPlan,
    DocumentationRequest,
    DocumentationTask,
)


class ProjectDocumentationPlanner(DocumentationPlanner):
    """Decomposes goals checking missing READMEs or APIs models."""

    def plan_documentation(
        self, request: DocumentationRequest, context: DocumentationContext
    ) -> DocumentationPlan:
        """Determines target documentation checklists.

        Args:
            request: Active request settings.
            context: Compiled context details.

        Returns:
            DocumentationPlan.
        """
        tasks = [
            DocumentationTask(
                id="doc-task-readme",
                target_name="README.md",
                task_type="readme",
                instructions="Generate baseline README.md containing overview, setup, and installation rules.",
            ),
            DocumentationTask(
                id="doc-task-api",
                target_name="FastAPI Routes",
                task_type="api",
                instructions="Document REST API routes controller endpoint details.",
            ),
            DocumentationTask(
                id="doc-task-architecture",
                target_name="System Architecture",
                task_type="architecture",
                instructions="Generate Mermaid component diagram and details describing project structure.",
            ),
        ]

        return DocumentationPlan(
            plan_id=f"doc-plan-{int(time.time())}",
            summary=request.prompt[:120],
            tasks=tasks,
            risk_level="low",
        )
