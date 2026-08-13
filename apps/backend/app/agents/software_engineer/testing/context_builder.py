"""Context Builder compiling repository summaries and style metrics context.
"""

from app.agents.software_engineer.testing.interfaces import ContextBuilder
from app.agents.software_engineer.testing.models import (
    TestRequest,
    TestingContext,
)
from app.agents.software_engineer.generator.style_analyzer import WorkspaceStyleAnalyzer


class TestingContextBuilder(ContextBuilder):
    """Assembles framework configurations and active symbols context."""

    def __init__(self) -> None:
        self.style_analyzer = WorkspaceStyleAnalyzer()

    def build_context(
        self, request: TestRequest, workspace_path: str
    ) -> TestingContext:
        """Collects files count, style settings, and naming conventions.

        Args:
            request: Active test request settings.
            workspace_path: Workspace absolute path.

        Returns:
            TestingContext.
        """
        style = self.style_analyzer.analyze_style(workspace_path)

        return TestingContext(
            workspace_root=workspace_path,
            target_module=request.file_path,
            existing_tests_count=0,
            related_symbols=[],
            style_guidelines=style.model_dump(),
        )
