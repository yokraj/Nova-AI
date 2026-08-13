"""VSCode Controller managing VS Code workspace opening, file editing, terminal, and debugging.
"""

from typing import Any, Dict


class VscodeController:
    """Automates VS Code IDE, opening project workspaces, creating/editing files, running terminal, and debugging."""

    def open_workspace(self, project_path: str) -> Dict[str, Any]:
        """Opens project workspace directory in VS Code."""
        return {
            "project_path": project_path,
            "window": f"VS Code - {project_path.split('\\')[-1]}",
            "status": "OPENED",
        }
