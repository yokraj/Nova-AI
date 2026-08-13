"""Class Documenter extracting class methods and properties signatures.
"""

import ast
import os
from typing import List

from app.agents.software_engineer.documentation.models import ClassDocument


class LocalClassDocumenter:
    """Parses modules to locate Python classes."""

    def document_classes(self, workspace_path: str, file_path: str) -> List[ClassDocument]:
        """Scans classes.

        Args:
            workspace_path: Absolute workspace root.
            file_path: Relative file path.

        Returns:
            List of ClassDocument.
        """
        docs: List[ClassDocument] = []
        abs_path = os.path.join(workspace_path, file_path)

        if not os.path.exists(abs_path):
            return docs

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(item.name)

                    docs.append(
                        ClassDocument(
                            name=node.name,
                            purpose=f"Python class definition representing {node.name}.",
                            methods=methods,
                            docstring=ast.get_docstring(node),
                        )
                    )
        except Exception:
            pass

        return docs
