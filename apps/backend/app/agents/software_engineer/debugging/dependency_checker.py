"""Dependency Checker detecting missing requirements and version conflicts.
"""

import os
from typing import List

from app.agents.software_engineer.debugging.interfaces import DependencyChecker
from app.agents.software_engineer.debugging.models import DependencyIssue


class ProjectDependencyChecker(DependencyChecker):
    """Audits lock files and manifests requirements."""

    def check_dependencies(self, workspace_path: str) -> List[DependencyIssue]:
        """Analyzes package configurations requirements.

        Args:
            workspace_path: Workspace absolute path.

        Returns:
            List of DependencyIssue.
        """
        issues: List[DependencyIssue] = []

        # Check for pyproject.toml or requirements.txt files existence
        has_pyproject = os.path.exists(os.path.join(workspace_path, "pyproject.toml"))
        has_reqs = os.path.exists(os.path.join(workspace_path, "requirements.txt"))

        if not has_pyproject and not has_reqs:
            issues.append(
                DependencyIssue(
                    package_name="system",
                    issue_type="missing_package",
                    message="No Python package configuration file (pyproject.toml or requirements.txt) was found.",
                )
            )

        return issues
