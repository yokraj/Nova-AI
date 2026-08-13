"""Failure Analyzer mapping traceback listings to assertions or import errors.
"""

import re
from app.agents.software_engineer.testing.interfaces import FailureAnalyzer
from app.agents.software_engineer.testing.models import FailureReport


class PytestFailureAnalyzer(FailureAnalyzer):
    """Categorizes failed assertions parsing stdout logs."""

    def analyze_failure(self, traceback_str: str) -> FailureReport:
        """Parses error output lines.

        Args:
            traceback_str: Traceback error output block.

        Returns:
            FailureReport.
        """
        failure_type = "runtime_exception"
        msg = traceback_str

        if "AssertionError" in traceback_str:
            failure_type = "assertion"
        elif "ImportError" in traceback_str or "ModuleNotFoundError" in traceback_str:
            failure_type = "import_error"
        elif "Timeout" in traceback_str:
            failure_type = "timeout"

        # Search for line numbers, e.g. "file.py:123:" or similar
        line_num = None
        match = re.search(r"\.py:(\d+):", traceback_str)
        if match:
            line_num = int(match.group(1))

        return FailureReport(
            failure_type=failure_type,
            message=msg[:300],  # truncate message
            traceback=traceback_str,
            failing_line_number=line_num,
        )
