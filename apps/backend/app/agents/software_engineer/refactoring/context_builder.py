"""Context Builder assembling files context and repository profiles.
"""

from app.agents.software_engineer.refactoring.interfaces import ContextBuilder
from app.agents.software_engineer.refactoring.models import (
    RefactoringContext,
    RefactoringRequest,
)
from app.agents.software_engineer.generator.style_analyzer import WorkspaceStyleAnalyzer


class RepositoryContextBuilder(ContextBuilder):
    """Gathers symbol listings and files content snapshot to form Context."""

    def __init__(self) -> None:
        self.style_analyzer = WorkspaceStyleAnalyzer()

    def build_context(
        self, request: RefactoringRequest, workspace_path: str
    ) -> RefactoringContext:
        """Assembles variables structure and style guides.

        Args:
            request: RefactoringRequest parameters.
            workspace_path: Absolute workspace root path.

        Returns:
            RefactoringContext.
        """
        style = self.style_analyzer.analyze_style(workspace_path)

        return RefactoringContext(
            workspace_root=workspace_path,
            target_file=request.file_path,
            symbol_definitions=[],
            style_guidelines=style.model_dump(),
            dependency_graph_summary={},
        )
