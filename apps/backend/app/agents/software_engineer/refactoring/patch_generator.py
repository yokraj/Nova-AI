"""Generates standardized patch files.
"""

import time
from typing import List

from app.agents.software_engineer.refactoring.interfaces import PatchGenerator
from app.agents.software_engineer.refactoring.models import DiffReport, PatchReport


class WorkspacePatchGenerator(PatchGenerator):
    """Merges unified diff strings to form single patch files."""

    def generate_patch(self, diffs: List[DiffReport]) -> PatchReport:
        """Assembles list of DiffReports.

        Args:
            diffs: List of DiffReport items.

        Returns:
            PatchReport payload.
        """
        contents = []
        affected = []

        for d in diffs:
            if d.unified_diff:
                contents.append(d.unified_diff)
                affected.append(d.file_path)

        patch_str = "\n".join(contents)
        patch_id = f"patch-{int(time.time())}"

        return PatchReport(
            patch_id=patch_id,
            patch_content=patch_str,
            affected_files=affected,
        )
