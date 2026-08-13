"""Snapshot Manager capturing backups before codebase modifications.
"""

import os
import time
from typing import List

from app.agents.software_engineer.refactoring.interfaces import SnapshotManager
from app.agents.software_engineer.refactoring.models import SnapshotInfo
from app.agents.software_engineer.refactoring.utils import backup_file


class WorkspaceSnapshotManager(SnapshotManager):
    """Saves and indexes snapshots in `.nova/refactor_snapshots/`."""

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self.workspace_root = workspace_root or os.getcwd()
        self.snapshots_dir = os.path.join(self.workspace_root, ".nova", "refactor_snapshots")

    def create_snapshot(
        self, workspace_path: str, file_paths: List[str]
    ) -> SnapshotInfo:
        """Copies file states inside a timestamp-named subdirectory.

        Args:
            workspace_path: Workspace absolute path root.
            file_paths: List of relative target file paths to back up.

        Returns:
            SnapshotInfo records.
        """
        snapshot_id = f"snap-{int(time.time() * 1000)}"
        session_backup_dir = os.path.join(self.snapshots_dir, snapshot_id)
        os.makedirs(session_backup_dir, exist_ok=True)

        backed_up = {}
        for rel_path in file_paths:
            abs_src = os.path.join(workspace_path, rel_path)
            if os.path.exists(abs_src):
                backup_dest = backup_file(abs_src, session_backup_dir, rel_path)
                backed_up[rel_path] = backup_dest

        return SnapshotInfo(
            snapshot_id=snapshot_id,
            timestamp=time.time(),
            workspace_root=workspace_path,
            backed_up_files=backed_up,
        )


from typing import Optional
