"""Real Workspace-Secured File Manager for Nova AI Desktop Automation.

Executes physical filesystem operations inside the authorized workspace boundary:
- Real file copy, move, duplicate, read, and delete operations.
- Workspace sandboxing via WorkspaceSecurityGuard.
- Exact byte tracking (never returns fabricated transfer statistics).
- Path traversal and unauthorized path rejection.
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import structlog

from app.ai.desktop_automation.models import FileOperation
from app.security.workspace_guard import (
    WorkspaceSecurityGuard,
    WorkspaceSecurityException,
)

logger = structlog.get_logger("file_manager")


class FileManager:
    """Performs real, verified file operations with workspace sandboxing and exact byte counts."""

    def __init__(self, workspace_guard: Optional[WorkspaceSecurityGuard] = None) -> None:
        self.guard = workspace_guard or WorkspaceSecurityGuard()

    def perform_file_operation(
        self, op_type: str, source_path: str, destination_path: Optional[str] = None
    ) -> FileOperation:
        """Executes a real filesystem operation within authorized workspace boundaries.

        Args:
            op_type: Operation type ('copy', 'move', 'read', 'duplicate', 'delete').
            source_path: Path to source file inside workspace.
            destination_path: Optional destination path inside workspace.

        Returns:
            FileOperation with real bytes transferred and verified path metadata.

        Raises:
            WorkspaceSecurityException: If either path escapes authorized workspace root.
            FileNotFoundError: If source file does not exist.
        """
        # Validate source path
        src = self.guard.resolve_workspace_path(source_path)
        dest: Optional[Path] = None
        if destination_path:
            dest = self.guard.resolve_workspace_path(destination_path)

        op = op_type.lower().strip()
        bytes_transferred: int = 0

        logger.info(
            "executing_file_operation",
            op=op,
            source=str(src),
            destination=str(dest) if dest else None,
        )

        if op in ("read", "inspect"):
            if not src.exists():
                raise FileNotFoundError(f"Source file not found: '{src}'")
            if not src.is_file():
                raise ValueError(f"Source is not a regular file: '{src}'")
            bytes_transferred = src.stat().st_size

        elif op == "copy":
            if not src.exists():
                raise FileNotFoundError(f"Source file not found: '{src}'")
            if not dest:
                raise ValueError("Destination path required for copy operation.")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            bytes_transferred = dest.stat().st_size

        elif op == "move":
            if not src.exists():
                raise FileNotFoundError(f"Source file not found: '{src}'")
            if not dest:
                raise ValueError("Destination path required for move operation.")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dest)
            bytes_transferred = dest.stat().st_size

        elif op == "duplicate":
            if not src.exists():
                raise FileNotFoundError(f"Source file not found: '{src}'")
            if not dest:
                # Generate copy name in same directory
                stem = src.stem
                suffix = src.suffix
                dest = src.parent / f"{stem}_copy{suffix}"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            bytes_transferred = dest.stat().st_size

        elif op in ("delete", "remove"):
            if not src.exists():
                raise FileNotFoundError(f"Source file not found: '{src}'")
            bytes_transferred = src.stat().st_size
            if src.is_file():
                src.unlink()
            elif src.is_dir():
                shutil.rmtree(src)

        else:
            # Default check / stat
            if src.exists():
                bytes_transferred = src.stat().st_size
            else:
                raise FileNotFoundError(f"Source file not found: '{src}'")

        return FileOperation(
            op_type=op,
            source_path=str(src),
            destination_path=str(dest) if dest else None,
            bytes_transferred=bytes_transferred,
        )
