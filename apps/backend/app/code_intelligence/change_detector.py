"""Change Detector Module.

Detects new, modified, deleted, and renamed files, as well as API route and database schema changes.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ChangeDetector:
    """Enterprise Source Code Delta & Change Detector."""

    def __init__(self) -> None:
        logger.info("change_detector_initialized")

    def detect_file_changes(
        self, old_file_hashes: Dict[str, str], new_file_hashes: Dict[str, str]
    ) -> Dict[str, List[str]]:
        """Compares file hashes to detect added, modified, and deleted files."""
        added = [f for f in new_file_hashes if f not in old_file_hashes]
        deleted = [f for f in old_file_hashes if f not in new_file_hashes]
        modified = [f for f in new_file_hashes if f in old_file_hashes and new_file_hashes[f] != old_file_hashes[f]]

        logger.info("file_changes_detected", added_count=len(added), modified_count=len(modified), deleted_count=len(deleted))
        return {
            "added_files": added,
            "modified_files": modified,
            "deleted_files": deleted,
        }
