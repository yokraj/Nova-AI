"""Scans files to locate syntax smells and refactoring candidate functions.
"""

import ast
import os
from typing import Any, Dict, List

from app.agents.software_engineer.refactoring.interfaces import RefactoringAnalyzer


class WorkspaceRefactoringAnalyzer(RefactoringAnalyzer):
    """Walks the filesystem and inspects Python AST trees to identify refactoring candidates."""

    def identify_opportunities(self, workspace_path: str) -> List[Dict[str, Any]]:
        """Scans python files recursively looking for smells (e.g. large methods, too many args).

        Args:
            workspace_path: Workspace directory root.

        Returns:
            List of dictionaries outlining locations, elements and recommended fixes.
        """
        opportunities = []
        py_files = []

        # Find python files (max 10 files to keep scan fast and bounded)
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
            rel_path = os.path.relpath(path, workspace_path)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()

                tree = ast.parse(code, filename=path)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Smell check 1: Large methods (more than 50 lines)
                        line_count = len(node.body)
                        if line_count > 50:
                            opportunities.append(
                                {
                                    "file": rel_path,
                                    "type": "long_method",
                                    "name": node.name,
                                    "severity": "medium",
                                    "description": f"Method '{node.name}' has {line_count} statement blocks.",
                                }
                            )
                        # Smell check 2: Too many parameters (more than 6 parameters)
                        param_count = len(node.args.args)
                        if param_count > 6:
                            opportunities.append(
                                {
                                    "file": rel_path,
                                    "type": "excessive_parameters",
                                    "name": node.name,
                                    "severity": "low",
                                    "description": f"Method '{node.name}' accepts {param_count} parameters.",
                                }
                            )
                    elif isinstance(node, ast.ClassDef):
                        # Smell check 3: Large classes (more than 15 methods)
                        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                        if len(methods) > 15:
                            opportunities.append(
                                {
                                    "file": rel_path,
                                    "type": "large_class",
                                    "name": node.name,
                                    "severity": "medium",
                                    "description": f"Class '{node.name}' contains {len(methods)} method declarations.",
                                }
                            )
            except Exception:
                continue

        return opportunities
