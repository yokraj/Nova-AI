"""Test Runner invoking local testing binaries.
"""

import os
import re
from typing import List

from app.agents.software_engineer.testing.interfaces import TestRunner
from app.agents.software_engineer.testing.models import TestResult, TestSuite
from app.agents.software_engineer.testing.utils import run_subprocess_command


class PytestTestRunner(TestRunner):
    """Executes pytest suites, parsing assertions outputs."""

    def run_tests(
        self, workspace_path: str, test_file_path: str
    ) -> TestSuite:
        """Invokes pytest binary in sub-processes capturing exit codes.

        Args:
            workspace_path: Absolute path to workspace root.
            test_file_path: Relative path of test target module.

        Returns:
            TestSuite.
        """
        # Run pytest inside the virtual environment
        cmd = ["uv", "run", "pytest", "-v", test_file_path]
        code, stdout, stderr = run_subprocess_command(cmd, workspace_path, timeout=45.0)

        # Parse test outcomes from stdout
        # Pytest output verbose has lines containing: tests/test_x.py::test_y PASSED
        results: List[TestResult] = []
        passed = 0
        failed = 0

        # Scan stdout line by line
        for line in stdout.splitlines():
            match = re.search(r"([a-zA-Z0-9_/.]+\.py::[a-zA-Z0-9_]+)\s+([A-Z]+)", line)
            if match:
                test_name, status = match.groups()
                if status == "PASSED":
                    results.append(TestResult(name=test_name, status="passed"))
                    passed += 1
                elif status in ("FAILED", "ERROR"):
                    results.append(TestResult(name=test_name, status="failed", error_message=line))
                    failed += 1

        # Fallback if pytest collected no items or parsing failed but it ran
        if not results:
            if code == 0:
                results.append(TestResult(name=test_file_path, status="passed"))
                passed = 1
            else:
                results.append(TestResult(name=test_file_path, status="failed", error_message=stderr or stdout))
                failed = 1

        return TestSuite(
            suite_name=test_file_path,
            results=results,
            passed_count=passed,
            failed_count=failed,
        )
