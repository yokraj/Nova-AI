"""Generates unified diff representation comparing original and modified files.
"""

from app.agents.software_engineer.refactoring.interfaces import DiffGenerator
from app.agents.software_engineer.refactoring.models import DiffReport
from app.agents.software_engineer.refactoring.utils import compute_unified_diff


class WorkspaceDiffGenerator(DiffGenerator):
    """Computes file changes list metrics."""

    def generate_diff(self, file_path: str, original: str, modified: str) -> DiffReport:
        """Runs difflib comparisons.

        Args:
            file_path: Relative target file path.
            original: Original file content.
            modified: Modified content.

        Returns:
            DiffReport.
        """
        diff_str = compute_unified_diff(original, modified, file_path)
        added = 0
        removed = 0

        # Calculate metrics
        for line in diff_str.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                added += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed += 1

        return DiffReport(
            file_path=file_path,
            unified_diff=diff_str,
            added_lines=added,
            removed_lines=removed,
        )
