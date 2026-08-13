"""Scans workspace source files to build stylistic guidelines profiles.
"""

import os
import re
from typing import List

from app.agents.software_engineer.generator.interfaces import StyleAnalyzer
from app.agents.software_engineer.generator.models import StyleProfile


class WorkspaceStyleAnalyzer(StyleAnalyzer):
    """Analyzes python source code in workspace to extract layout conventions."""

    def analyze_style(self, workspace_path: str) -> StyleProfile:
        """Scans workspace python files and compiles StyleProfile attributes.

        Args:
            workspace_path: Workspace directory path.

        Returns:
            StyleProfile model.
        """
        indentation = "    "
        naming_class = "PascalCase"
        naming_func = "snake_case"
        doc_format = "google"

        # Scan a few python files in workspace (max 5)
        py_files: List[str] = []
        for root, _, files in os.walk(workspace_path):
            if ".venv" in root or ".git" in root or "node_modules" in root:
                continue
            for f in files:
                if f.endswith(".py") and not f.startswith("__"):
                    py_files.append(os.path.join(root, f))
                    if len(py_files) >= 5:
                        break
            if len(py_files) >= 5:
                break

        if not py_files:
            return StyleProfile()

        space_indents = 0
        tab_indents = 0
        indent_lengths = []

        for f_path in py_files:
            try:
                with open(f_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # 1. Check Indentation
                for line in content.splitlines():
                    match = re.match(r"^(\s+)\S", line)
                    if match:
                        indent_str = match.group(1)
                        if "\t" in indent_str:
                            tab_indents += 1
                        else:
                            space_indents += 1
                            indent_lengths.append(len(indent_str))

                # 2. Check Naming Conventions (simple checks)
                # Find function names
                funcs = re.findall(r"def\s+([a-zA-Z0-9_]+)\(", content)
                for func in funcs:
                    if "_" in func:
                        naming_func = "snake_case"
                    elif func[0].islower() and not func.islower() and "_" not in func:
                        naming_func = "camelCase"

                # Find class names
                classes = re.findall(r"class\s+([a-zA-Z0-9_]+)", content)
                for cls in classes:
                    if "_" in cls:
                        naming_class = "snake_case"
                    else:
                        naming_class = "PascalCase"

                # Check docstring style
                if '"""' in content:
                    doc_format = "google"
            except Exception:
                continue

        # Resolve indentation preference
        if tab_indents > space_indents:
            indentation = "\t"
        elif indent_lengths:
            # Mode of indent lengths
            most_common_len = max(set(indent_lengths), key=indent_lengths.count)
            indentation = " " * most_common_len

        return StyleProfile(
            indentation=indentation,
            naming_convention_class=naming_class,
            naming_convention_function=naming_func,
            docstring_format=doc_format,
        )
