"""Code Documenter analyzing files to extract class and function profiles.
"""

from app.agents.software_engineer.documentation.interfaces import CodeDocumenter
from app.agents.software_engineer.documentation.models import CodeDocument, ModuleDocument
from app.agents.software_engineer.documentation.class_documenter import LocalClassDocumenter
from app.agents.software_engineer.documentation.function_documenter import LocalFunctionDocumenter


class WorkspaceCodeDocumenter(CodeDocumenter):
    """Parses modules extracting structural metadata."""

    def __init__(self) -> None:
        self.class_doc = LocalClassDocumenter()
        self.func_doc = LocalFunctionDocumenter()

    def document_code(
        self, workspace_path: str, file_path: str
    ) -> CodeDocument:
        """Parses files to build details.

        Args:
            workspace_path: Absolute workspace root.
            file_path: Relative file path.

        Returns:
            CodeDocument.
        """
        # Call specific subcomponents
        classes = self.class_doc.document_classes(workspace_path, file_path)
        functions = self.func_doc.document_functions(workspace_path, file_path)

        mod_doc = ModuleDocument(
            file_path=file_path,
            purpose=f"Code level documentation logs for {file_path}.",
            classes=classes,
            functions=functions,
        )

        return CodeDocument(modules=[mod_doc])
