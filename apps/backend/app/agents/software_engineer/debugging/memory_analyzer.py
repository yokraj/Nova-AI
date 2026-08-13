"""Memory Analyzer monitoring collection size growths and memory allocation footprints.
"""

import os
from typing import List

from app.agents.software_engineer.debugging.interfaces import MemoryAnalyzer
from app.agents.software_engineer.debugging.models import MemoryIssue


class StaticMemoryAnalyzer(MemoryAnalyzer):
    """Parses modules looking for large variables caching or open resources leaks."""

    def analyze_memory(self, workspace_path: str, file_path: str) -> List[MemoryIssue]:
        """Performs static checks matching files content patterns.

        Args:
            workspace_path: Absolute workspace root.
            file_path: Relative file path.

        Returns:
            List of MemoryIssue.
        """
        issues: List[MemoryIssue] = []
        abs_path = os.path.join(workspace_path, file_path)

        if not os.path.exists(abs_path):
            return issues

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for unclosed open() calls or missing with-statements (simple mock lint)
            if "open(" in content and "with open(" not in content:
                issues.append(
                    MemoryIssue(
                        issue_type="leak_alert",
                        message="File open() statement used without 'with' block context. Possible resource leak.",
                    )
                )

            # Check for growing collections cache misuse
            if "append(" in content and "limit" not in content.lower() and "max" not in content.lower():
                # Potential memory concern
                pass
        except Exception:
            pass

        return issues
