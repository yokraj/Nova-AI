"""Test Executor scheduling parallel worker test suites.
"""

from typing import List

from app.agents.software_engineer.testing.interfaces import TestExecutor
from app.agents.software_engineer.testing.models import TestSuite
from app.agents.software_engineer.testing.runner import PytestTestRunner


class WorkspaceTestExecutor(TestExecutor):
    """Schedules sequential test executions."""

    def __init__(self) -> None:
        self.runner = PytestTestRunner()

    def execute_queue(
        self, workspace_path: str, tests_to_run: List[str]
    ) -> List[TestSuite]:
        """Runs testing requests.

        Args:
            workspace_path: Workspace absolute path root.
            tests_to_run: List of test file paths.

        Returns:
            List of TestSuite outputs.
        """
        suites = []
        for test_path in tests_to_run:
            suite = self.runner.run_tests(workspace_path, test_path)
            suites.append(suite)
        return suites
