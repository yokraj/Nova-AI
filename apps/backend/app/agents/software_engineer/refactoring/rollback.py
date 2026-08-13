"""Rollback Manager restoring code to previous backup states.
"""

import os
from typing import Optional

from app.agents.software_engineer.refactoring.interfaces import RollbackManager
from app.agents.software_engineer.refactoring.models import RollbackResult
from app.agents.software_engineer.refactoring.utils import restore_file


class WorkspaceRollbackManager(RollbackManager):
    """Restores snapshots from `.nova/refactor_snapshots/`."""

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self.workspace_root = workspace_root or os.getcwd()
        self.snapshots_dir = os.path.join(self.workspace_root, ".nova", "refactor_snapshots")

    def rollback(self, snapshot_id: str) -> RollbackResult:
        """Overwrites modified target files using copy operations from snapshot directory.

        Args:
            snapshot_id: Target snapshot session id.

        Returns:
            RollbackResult payload status details.
        """
        session_dir = os.path.join(self.snapshots_dir, snapshot_id)
        if not os.path.exists(session_dir):
            return RollbackResult(
                success=False,
                snapshot_id=snapshot_id,
                errors=[f"Snapshot session path '{session_dir}' not found."],
            )

        restored = []
        errors = []

        # Recursively walk backup files and copy them back
        for root, _, files in os.walk(session_dir):
            for f in files:
                abs_backup_path = os.path.join(root, f)
                # Compute relative path from snapshot base
                rel_path = os.path.relpath(abs_backup_path, session_dir)
                abs_orig_path = os.path.join(self.workspace_root, rel_path)

                try:
                    restore_file(abs_backup_path, abs_orig_path)
                    restored.append(rel_path)
                except Exception as e:
                    errors.append(f"Failed to restore '{rel_path}': {str(e)}")

        return RollbackResult(
            success=len(errors) == 0,
            snapshot_id=snapshot_id,
            restored_files=restored,
            errors=errors,
        )
