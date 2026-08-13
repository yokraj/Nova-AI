"""Test Planner prioritizing test runs based on code risks and file modifications.
"""

import os
import time
from app.agents.software_engineer.testing.interfaces import TestPlanner
from app.agents.software_engineer.testing.models import (
    TestPlan,
    TestRequest,
    TestTask,
    TestingContext,
)


class WorkspaceTestPlanner(TestPlanner):
    """Identifies test targets, prioritizing based on project configurations."""

    def plan_testing(
        self, request: TestRequest, context: TestingContext
    ) -> TestPlan:
        """Determines files or structures requiring testing suites.

        Args:
            request: Testing request parameters.
            context: Workspace context.

        Returns:
            TestPlan.
        """
        target = request.file_path or "app/main.py"
        base_name = os.path.basename(target)
        test_file = f"tests/test_{base_name}"

        task = TestTask(
            id="test-task-1",
            target_module=target,
            test_type="unit",
            instructions=f"Generate unit tests suite inside '{test_file}' for: {request.prompt}",
            dependencies=[],
            status="pending",
        )

        return TestPlan(
            plan_id=f"test-plan-{int(time.time())}",
            request_summary=request.prompt[:100],
            tasks=[task],
            risk_profile="medium",
        )
