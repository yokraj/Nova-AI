"""Environment Checker validating environment paths and manifest settings.
"""

import os
from typing import Any, Dict


class ProjectEnvironmentChecker:
    """Verifies that the target execution workspace is fully configured."""

    def check_environment(self, workspace_path: str) -> Dict[str, Any]:
        """Audits python paths, locks, and environment setups.

        Args:
            workspace_path: Workspace absolute path root.

        Returns:
            Dict mapping audit keys to status strings.
        """
        status = {
            "pythonpath_defined": "PYTHONPATH" in os.environ,
            "has_virtual_environment": False,
        }

        # Check virtual environments directories
        for folder in (".venv", "venv", "env"):
            if os.path.exists(os.path.join(workspace_path, folder)):
                status["has_virtual_environment"] = True
                break

        return status
