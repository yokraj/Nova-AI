"""Decomposes refactoring directives into sequence plans.
"""

from typing import List

from app.agents.software_engineer.refactoring.interfaces import RefactoringPlanner
from app.agents.software_engineer.refactoring.models import (
    RefactoringContext,
    RefactoringPlan,
    RefactoringRequest,
    RefactoringTask,
)


class WorkspaceRefactoringPlanner(RefactoringPlanner):
    """Compiles task dependency chains for requested modifications."""

    def plan_refactoring(
        self, request: RefactoringRequest, context: RefactoringContext
    ) -> RefactoringPlan:
        """Constructs list of files and operational steps needed.

        Args:
            request: The refactoring directive request.
            context: Collected context environment.

        Returns:
            RefactoringPlan model.
        """
        target = request.file_path or "refactored_code.py"
        action = request.refactor_type or "modernize"

        task = RefactoringTask(
            id="ref-task-1",
            action=action,
            target_file=target,
            instructions=request.prompt,
            dependencies=[],
            status="pending",
        )

        return RefactoringPlan(
            plan_id=f"ref-plan-{int(time.time())}",
            request_summary=request.prompt[:100],
            tasks=[task],
            estimated_risk="medium",
            affected_files=[target],
        )


import time
