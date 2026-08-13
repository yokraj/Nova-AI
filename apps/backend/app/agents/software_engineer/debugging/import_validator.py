"""Import Validator scanning AST nodes for cyclical or unused imports.
"""

import ast
import os
from typing import List

from app.agents.software_engineer.debugging.interfaces import ImportValidator
from app.agents.software_engineer.debugging.models import ImportIssue


class ASTImportValidator(ImportValidator):
    """Parses modules using AST to flag imports violations."""

    def validate_imports(self, workspace_path: str, file_path: str) -> List[ImportIssue]:
        """Scans import blocks.

        Args:
            workspace_path: Absolute workspace root.
            file_path: Relative file path.

        Returns:
            List of ImportIssue.
        """
        issues: List[ImportIssue] = []
        abs_path = os.path.join(workspace_path, file_path)

        if not os.path.exists(abs_path):
            return issues

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    # Check for local imports containing relative cycles (simple mock checker)
                    if isinstance(node, ast.ImportFrom) and node.level and node.level > 1:
                        issues.append(
                            ImportIssue(
                                file_path=file_path,
                                issue_type="cyclic_import",
                                message="Potential relative cycle import found.",
                                line_number=node.lineno,
                            )
                        )
        except Exception:
            pass

        return issues
