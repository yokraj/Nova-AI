"""Context Manager gathers active workspace profiles and history variables.
"""

import os
from typing import Optional
from app.agents.software_engineer.autonomous.models import ExecutionContext
from app.agents.software_engineer.repository.analyzer import RepositoryAnalyzer

class ContextManager:
    """Consolidates repository contexts and intent variables."""

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self.workspace_root = workspace_root or os.getcwd()
        self.repo_analyzer = RepositoryAnalyzer(workspace_root=self.workspace_root)

    def build_context(self, user_intent: str) -> ExecutionContext:
        """Gathers branch, project, and file metadata context."""
        branch = None
        try:
            branches = self.repo_analyzer.analyze_branches()
            if branches:
                branch = branches[0]
        except Exception:
            pass

        return ExecutionContext(
            workspace_root=self.workspace_root,
            project_name=os.path.basename(self.workspace_root) or "app",
            git_branch=branch,
            history_actions=[f"Processed user intent: {user_intent}"]
        )
