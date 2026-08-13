"""Codebase Analyzer inspecting source files for undocumented functions.
"""

import ast
import os
from typing import List


class WorkspaceDocumentationAnalyzer:
    """Detects missing documentation in classes and method nodes."""

    def find_undocumented_symbols(self, workspace_path: str) -> List[str]:
        """Scans workspace python files locating function and class definitions missing docstrings.

        Args:
            workspace_path: Absolute target workspace root path.

        Returns:
            List of undocumented symbols names.
        """
        undocumented = []

        # Gather target py files (max 10)
        py_files = []
        for root, _, files in os.walk(workspace_path):
            if ".venv" in root or ".git" in root or "node_modules" in root:
                continue
            for f in files:
                if f.endswith(".py") and not f.startswith("__"):
                    py_files.append(os.path.join(root, f))
                    if len(py_files) >= 10:
                        break
            if len(py_files) >= 10:
                break

        for path in py_files:
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    tree = ast.parse(f.read(), filename=path)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        doc = ast.get_docstring(node)
                        if not doc:
                            undocumented.append(f"{os.path.basename(path)}::{node.name}")
            except Exception:
                continue

        return undocumented
