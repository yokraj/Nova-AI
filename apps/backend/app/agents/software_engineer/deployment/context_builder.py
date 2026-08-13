"""Deployment Context Builder gathers codebase structures for configuration generation.
"""

import os
from typing import Any, Dict, List, Optional
from app.agents.software_engineer.repository.analyzer import RepositoryAnalyzer
from app.agents.software_engineer.intelligence.analyzer import CodeIntelligenceAnalyzer

class DeploymentContextBuilder:
    """Builds structural code context for the deployment planner."""

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self.workspace_root = workspace_root or os.getcwd()
        self.repo_analyzer = RepositoryAnalyzer(workspace_root=self.workspace_root)
        self.code_intel = CodeIntelligenceAnalyzer(workspace_root=self.workspace_root)

    def build_context(self) -> Dict[str, Any]:
        """Gathers branch, history, and workspace files details."""
        files = []
        for root, _, filenames in os.walk(self.workspace_root):
            # Skip common ignores
            if any(ignore in root for ignore in [".git", ".venv", "__pycache__", "node_modules", "build", "dist"]):
                continue
            for f in filenames:
                rel_path = os.path.relpath(os.path.join(root, f), self.workspace_root)
                files.append(rel_path)

        branches = []
        try:
            branches = self.repo_analyzer.analyze_branches()
        except Exception:
            pass

        return {
            "workspace_root": self.workspace_root,
            "files": files,
            "branches": branches,
            "project_name": os.path.basename(self.workspace_root),
        }
