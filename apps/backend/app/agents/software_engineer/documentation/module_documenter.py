"""Module Documenter organizing class and function documentation targets.
"""

import os
from typing import List

from app.agents.software_engineer.documentation.class_documenter import LocalClassDocumenter
from app.agents.software_engineer.documentation.function_documenter import LocalFunctionDocumenter
from app.agents.software_engineer.documentation.models import ModuleDocument


class LocalModuleDocumenter:
    """Consolidates document representations of individual source files."""

    def __init__(self) -> None:
        self.class_doc = LocalClassDocumenter()
        self.func_doc = LocalFunctionDocumenter()

    def document_module(self, workspace_path: str, file_path: str) -> ModuleDocument:
        """Parses files.

        Args:
            workspace_path: Absolute workspace root.
            file_path: Relative file path.

        Returns:
            ModuleDocument.
        """
        classes = self.class_doc.document_classes(workspace_path, file_path)
        functions = self.func_doc.document_functions(workspace_path, file_path)

        return ModuleDocument(
            file_path=file_path,
            purpose=f"Module summary detailing contents of {file_path}.",
            classes=classes,
            functions=functions,
        )
