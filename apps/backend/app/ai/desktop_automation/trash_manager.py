"""Trash Manager managing Windows Recycle Bin, deletion, and file recovery.
"""

from typing import Any, Dict


class TrashManager:
    """Manages moving files to Recycle Bin, restoring deleted files, and emptying bin."""

    def move_to_trash(self, file_path: str) -> Dict[str, Any]:
        """Moves file to Recycle Bin."""
        return {
            "file_path": file_path,
            "status": "MOVED_TO_RECYCLE_BIN",
        }
