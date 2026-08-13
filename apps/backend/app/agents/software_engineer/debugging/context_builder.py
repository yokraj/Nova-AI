"""Context Builder compiling active settings details and file structures.
"""

import os
from typing import Dict, List, Optional
from app.agents.software_engineer.debugging.models import DebugContext, DebugRequest


class DebugContextBuilder:
    """Assembles repository file parameters and environment configurations."""

    def build_context(
        self, request: DebugRequest, workspace_path: str
    ) -> DebugContext:
        """Gathers workspace metadata.

        Args:
            request: Current request details.
            workspace_path: Absolute target directory root path.

        Returns:
            DebugContext.
        """
        # Count source files in workspace
        file_count = 0
        for root, _, files in os.walk(workspace_path):
            if ".venv" in root or ".git" in root or "node_modules" in root:
                continue
            file_count += len([f for f in files if f.endswith(".py")])

        # Filter safe environmental variables
        env_vars = {}
        for k in ("PYTHONPATH", "PATH", "APP_ENV", "PORT"):
            if k in os.environ:
                env_vars[k] = os.environ[k]

        return DebugContext(
            workspace_root=workspace_path,
            scanned_files_count=file_count,
            related_symbols=[],
            environment_variables=env_vars,
        )
