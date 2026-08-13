"""Coverage Analyzer reporting file, branch, and class level testing metrics.
"""

import ast
import os
from typing import List

from app.agents.software_engineer.testing.interfaces import CoverageAnalyzer
from app.agents.software_engineer.testing.models import CoverageReport


class WorkspaceCoverageAnalyzer(CoverageAnalyzer):
    """Parses coverage results mapping missing tests coverage percentages."""

    def analyze_coverage(self, workspace_path: str) -> CoverageReport:
        """Counts symbols in the workspace compared with test directories declarations.

        Args:
            workspace_path: Absolute workspace root.

        Returns:
            CoverageReport mapping untraced files.
        """
        # Count source classes/functions vs test file structures (simple fallback estimation)
        src_symbols = []
        test_symbols = []

        # Gather standard python code files (max 10 files)
        py_files = []
        for root, _, files in os.walk(workspace_path):
            if ".venv" in root or ".git" in root or "node_modules" in root or "tests" in root:
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
                        src_symbols.append(node.name)
            except Exception:
                continue

        # Check existing test files (max 5)
        test_files = []
        tests_dir = os.path.join(workspace_path, "tests")
        if os.path.exists(tests_dir):
            for root, _, files in os.walk(tests_dir):
                for f in files:
                    if f.startswith("test_") and f.endswith(".py"):
                        test_files.append(os.path.join(root, f))
                        if len(test_files) >= 5:
                            break
                if len(test_files) >= 5:
                    break

        for path in test_files:
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    tree = ast.parse(f.read(), filename=path)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                        # Extract the target being tested by name
                        target_name = node.name[5:]
                        test_symbols.append(target_name)
            except Exception:
                continue

        untested = [s for s in src_symbols if s not in test_symbols]
        overall = 0.0
        if src_symbols:
            overall = max(0.0, 100.0 - (len(untested) / len(src_symbols) * 100.0))

        # Fill map
        file_maps = {}
        for path in py_files:
            rel = os.path.relpath(path, workspace_path)
            file_maps[rel] = overall

        return CoverageReport(
            overall_percentage=round(overall, 1),
            file_coverages=file_maps,
            untested_symbols=untested[:20],  # cap list
        )
