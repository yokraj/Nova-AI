"""Transforms Python AST structures preserving comments and signatures where possible.
"""

import ast
from typing import Any

from app.agents.software_engineer.refactoring.interfaces import CodeTransformer


class WorkspaceCodeTransformer(CodeTransformer):
    """Parses and updates Python source syntax nodes."""

    def transform_ast(self, file_path: str, transformer_node: Any) -> str:
        """Runs node transformations on the target python file content.

        Args:
            file_path: Relative source target file path.
            transformer_node: NodeTransformer subclass instance.

        Returns:
            Regenerated python code content string.
        """
        # Read the file
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        # Build AST
        tree = ast.parse(source, filename=file_path)

        # Apply transformation
        modified_tree = transformer_node.visit(tree)
        ast.fix_missing_locations(modified_tree)

        # Unparse back to string source
        return ast.unparse(modified_tree)
