"""Assembles repository, AST, and styling parameters context to guide models generation.
"""

from app.agents.software_engineer.generator.interfaces import ContextBuilder
from app.agents.software_engineer.generator.models import (
    ContextSummary,
    GenerationContext,
    GenerationRequest,
)
from app.agents.software_engineer.generator.style_analyzer import WorkspaceStyleAnalyzer


class RepositoryContextBuilder(ContextBuilder):
    """Builds context packages representing codebase state."""

    def __init__(self) -> None:
        self.style_analyzer = WorkspaceStyleAnalyzer()

    def build_context(
        self, request: GenerationRequest, workspace_path: str
    ) -> GenerationContext:
        """Collects repository statistics, symbol mappings, and coding styles.

        Args:
            request: GenerationRequest configuration details.
            workspace_path: Absolute path to workspace root.

        Returns:
            GenerationContext model.
        """
        # 1. Analyze style
        style = self.style_analyzer.analyze_style(workspace_path)

        # 2. Get repository summaries and imports details (placeholders/mock stats to fit limits)
        related_files = []
        if request.file_path:
            related_files.append(request.file_path)

        # Build Context Summary
        summary = ContextSummary(
            repository_summary=f"Python codebase located at '{workspace_path}'",
            related_files=related_files,
            similar_symbols=[],
            token_count_estimation=100,
        )

        return GenerationContext(
            workspace_root=workspace_path,
            summary=summary,
            style_profile=style,
            code_intelligence_summary={
                "language": "python",
                "framework": "FastAPI",
            },
        )
