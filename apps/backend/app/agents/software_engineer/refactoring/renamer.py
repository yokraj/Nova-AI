"""Renames variables, functions, and classes across the codebase targets.
"""

import ast
import os
from typing import List

from app.agents.software_engineer.refactoring.interfaces import SymbolRenamer
from app.agents.software_engineer.refactoring.models import SymbolRenameResult


class ASTSymbolRenamer(ast.NodeTransformer):
    """Subclass visitor that renames all target name occurrences."""

    def __init__(self, old_name: str, new_name: str) -> None:
        self.old_name = old_name
        self.new_name = new_name
        self.replaced_count = 0

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if node.id == self.old_name:
            node.id = self.new_name
            self.replaced_count += 1
        return self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        if node.name == self.old_name:
            node.name = self.new_name
            self.replaced_count += 1
        return self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        if node.name == self.old_name:
            node.name = self.new_name
            self.replaced_count += 1
        return self.generic_visit(node)


class WorkspaceSymbolRenamer(SymbolRenamer):
    """Scans and renames references of a symbol project-wide."""

    def rename_symbol(
        self, workspace_path: str, file_path: str, old_name: str, new_name: str
    ) -> SymbolRenameResult:
        """Applies SymbolRenamer node transformer to target file path.

        Args:
            workspace_path: Workspace absolute path.
            file_path: Relative path of file to modify.
            old_name: Target symbol name.
            new_name: Proposed name.

        Returns:
            SymbolRenameResult.
        """
        abs_path = os.path.join(workspace_path, file_path)
        if not os.path.exists(abs_path):
            return SymbolRenameResult(success=False, symbol_name=old_name, new_name=new_name)

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=abs_path)
            renamer = ASTSymbolRenamer(old_name, new_name)
            modified_tree = renamer.visit(tree)
            ast.fix_missing_locations(modified_tree)

            new_source = ast.unparse(modified_tree)

            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_source)

            return SymbolRenameResult(
                success=True,
                symbol_name=old_name,
                new_name=new_name,
                occurrences_replaced=renamer.replaced_count,
            )
        except Exception:
            return SymbolRenameResult(success=False, symbol_name=old_name, new_name=new_name)
