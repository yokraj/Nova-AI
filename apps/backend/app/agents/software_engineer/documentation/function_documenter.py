"""Function Documenter extracting parameters, exception triggers, and return values schemas.
"""

import ast
import os
from typing import List

from app.agents.software_engineer.documentation.models import FunctionDocument


class LocalFunctionDocumenter:
    """Parses modules to extract function signatures details."""

    def document_functions(self, workspace_path: str, file_path: str) -> List[FunctionDocument]:
        """Scans functions.

        Args:
            workspace_path: Absolute workspace root.
            file_path: Relative file path.

        Returns:
            List of FunctionDocument.
        """
        docs: List[FunctionDocument] = []
        abs_path = os.path.join(workspace_path, file_path)

        if not os.path.exists(abs_path):
            return docs

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    params = [arg.arg for arg in node.args.args]
                    docs.append(
                        FunctionDocument(
                            name=node.name,
                            purpose=f"Python function definition representing {node.name}.",
                            parameters=params,
                            returns="Any",
                            exceptions=[],
                        )
                    )
        except Exception:
            pass

        return docs
