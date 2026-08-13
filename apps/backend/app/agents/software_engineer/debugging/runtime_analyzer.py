"""Runtime Analyzer inspecting trace logs for async and middleware failures.
"""

from typing import List

from app.agents.software_engineer.debugging.interfaces import RuntimeAnalyzer
from app.agents.software_engineer.debugging.models import RuntimeIssue


class LocalRuntimeAnalyzer(RuntimeAnalyzer):
    """Parses application logs warnings."""

    def analyze_runtime(self, log_lines: List[str]) -> List[RuntimeIssue]:
        """Scans log lines.

        Args:
            log_lines: Log output lines list.

        Returns:
            List of RuntimeIssue.
        """
        issues: List[RuntimeIssue] = []

        for line in log_lines:
            line_lower = line.lower()
            if "cancellederror" in line_lower:
                issues.append(
                    RuntimeIssue(
                        issue_type="task_cancellation",
                        message="Async task cancellation warning logged.",
                    )
                )
            elif "timeout" in line_lower:
                issues.append(
                    RuntimeIssue(
                        issue_type="async_timeout",
                        message="Async event loop timeout limit hit.",
                    )
                )

        return issues
