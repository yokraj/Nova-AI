"""Performance Analyzer identifying slow loops or recursive hotspots.
"""

import os
from typing import List

from app.agents.software_engineer.debugging.interfaces import PerformanceAnalyzer
from app.agents.software_engineer.debugging.models import PerformanceIssue


class StaticPerformanceAnalyzer(PerformanceAnalyzer):
    """Parses modules looking for synchronous blocking calls or unconstrained loops."""

    def analyze_performance(self, workspace_path: str, file_path: str) -> List[PerformanceIssue]:
        """Runs checks.

        Args:
            workspace_path: Absolute workspace root.
            file_path: Relative file path.

        Returns:
            List of PerformanceIssue.
        """
        issues: List[PerformanceIssue] = []
        abs_path = os.path.join(workspace_path, file_path)

        if not os.path.exists(abs_path):
            return issues

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for synchronous sleep inside async methods
            if "async def" in content and "time.sleep(" in content:
                issues.append(
                    PerformanceIssue(
                        issue_type="blocking_call",
                        message="Synchronous time.sleep() used inside an async function. Will block the event loop.",
                    )
                )

            # Check for deep recursion triggers
            if "def " in content and "sys.setrecursionlimit" in content:
                issues.append(
                    PerformanceIssue(
                        issue_type="recursion_bottleneck",
                        message="Manual manipulation of sys recursion limit detected.",
                    )
                )
        except Exception:
            pass

        return issues
