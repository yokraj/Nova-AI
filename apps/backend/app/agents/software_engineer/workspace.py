"""WorkspaceManager handling path verification and file listings in workspace directories.
"""

import os
from typing import Any, Dict, List, Optional

from app.agents.software_engineer.exceptions import WorkspaceError
from app.agents.software_engineer.interfaces import IWorkspaceManager


class WorkspaceManager(IWorkspaceManager):
    """Manages read-only checks and files listings in the workspace directory."""

    def __init__(self) -> None:
        """Initializes WorkspaceManager."""
        self._path: Optional[str] = None

    def open_workspace(self, path: str) -> None:
        """Opens and validates target workspace directory path.

        Args:
            path: Target directory.

        Raises:
            WorkspaceError: If path is empty, non-existent, or not a directory.
        """
        if not path:
            raise WorkspaceError("Workspace path cannot be empty.")
        if not os.path.exists(path):
            raise WorkspaceError(f"Workspace path '{path}' does not exist.")
        if not os.path.isdir(path):
            raise WorkspaceError(f"Workspace path '{path}' is not a directory.")
        self._path = os.path.abspath(path)

    def close_workspace(self) -> None:
        """Closes the current workspace."""
        self._path = None

    def current_workspace(self) -> Optional[str]:
        """Gets active workspace path.

        Returns:
            String path, or None.
        """
        return self._path

    def list_files(self) -> List[str]:
        """Lists files inside the active workspace directory recursively.

        Returns:
            List of relative file paths.

        Raises:
            WorkspaceError: If no workspace is open.
        """
        if not self._path:
            raise WorkspaceError("No workspace is currently open.")

        file_list = []
        for root, _, files in os.walk(self._path):
            for file in files:
                abs_file = os.path.join(root, file)
                rel_file = os.path.relpath(abs_file, self._path)
                file_list.append(rel_file)
        return file_list

    def workspace_information(self) -> Dict[str, Any]:
        """Exposes metadata metrics about the active workspace.

        Returns:
            Dictionary containing files count and directory statistics.

        Raises:
            WorkspaceError: If details resolution fails.
        """
        if not self._path:
            return {"status": "closed"}
        try:
            files = self.list_files()
            return {
                "status": "open",
                "workspace_root": self._path,
                "total_files": len(files),
            }
        except Exception as e:
            raise WorkspaceError(f"Failed to fetch workspace information: {str(e)}") from e

    def validate_workspace(self) -> bool:
        """Validates that workspace directory is readable.

        Returns:
            True if valid, raises WorkspaceError otherwise.

        Raises:
            WorkspaceError: If workspace not open or not readable.
        """
        if not self._path:
            raise WorkspaceError("No workspace is currently open.")
        if not os.access(self._path, os.R_OK):
            raise WorkspaceError(f"Workspace directory '{self._path}' is not readable.")
        return True
