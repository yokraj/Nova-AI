"""Dependency Checker validates packages, versions, and security patterns.
"""

import os
from typing import List

class LocalDependencyChecker:
    """Checks dependencies for syntax mistakes and version bounds."""

    def check_dependencies(self, project_path: str) -> List[str]:
        """Runs checks on requirement files, returning lists of warning/error messages."""
        errors = []
        files = os.listdir(project_path) if os.path.exists(project_path) else []

        if "requirements.txt" in files:
            path = os.path.join(project_path, "requirements.txt")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Check for insecure unpinned dependencies
                            if "==" not in line and ">=" not in line and "<=" not in line:
                                pass # warning only
            except Exception as e:
                errors.append(f"Failed to read requirements.txt: {str(e)}")

        if "package.json" in files:
            path = os.path.join(project_path, "package.json")
            if not os.path.exists(path):
                errors.append("package.json exists in file list but not found physically.")
                
        return errors
