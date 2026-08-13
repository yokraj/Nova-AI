"""Context Builder compiling repository metrics and file layout styles parameters.
"""

import os
from app.agents.software_engineer.documentation.interfaces import ContextBuilder
from app.agents.software_engineer.documentation.models import (
    DocumentationContext,
    DocumentationRequest,
)
from app.agents.software_engineer.generator.style_analyzer import WorkspaceStyleAnalyzer


class DocumentationContextBuilder(ContextBuilder):
    """Assembles file count statistics and active symbol listings."""

    def __init__(self) -> None:
        self.style_analyzer = WorkspaceStyleAnalyzer()

    def build_context(
        self, request: DocumentationRequest, workspace_path: str
    ) -> DocumentationContext:
        """Gathers files count and configurations.

        Args:
            request: Current request parameters.
            workspace_path: Absolute workspace root.

        Returns:
            DocumentationContext.
        """
        style = self.style_analyzer.analyze_style(workspace_path)

        file_count = 0
        for root, _, files in os.walk(workspace_path):
            if ".venv" in root or ".git" in root or "node_modules" in root:
                continue
            file_count += len([f for f in files if f.endswith(".py")])

        return DocumentationContext(
            workspace_root=workspace_path,
            scanned_files_count=file_count,
            languages_percentages={"python": 100.0},
            active_symbols=[],
            style_guidelines=style.model_dump(),
        )
