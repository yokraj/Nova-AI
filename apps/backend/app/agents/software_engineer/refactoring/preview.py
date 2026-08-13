"""Previews refactoring operations before committing code modifications.
"""

from app.agents.software_engineer.refactoring.interfaces import PreviewProvider
from app.agents.software_engineer.refactoring.models import (
    ConflictReport,
    RefactoringContext,
    RefactoringPreview,
    RefactoringRequest,
)
from app.agents.software_engineer.refactoring.planner import WorkspaceRefactoringPlanner
from app.agents.software_engineer.refactoring.conflict_detector import WorkspaceConflictDetector


class WorkspacePreviewProvider(PreviewProvider):
    """Compiles dry-run reports previews."""

    def __init__(self) -> None:
        self.planner = WorkspaceRefactoringPlanner()
        self.conflict_detector = WorkspaceConflictDetector()

    def generate_preview(
        self, request: RefactoringRequest, context: RefactoringContext
    ) -> RefactoringPreview:
        """Assembles risk and diff checks reports.

        Args:
            request: Refactoring request.
            context: Collected context.

        Returns:
            RefactoringPreview report.
        """
        plan = self.planner.plan_refactoring(request, context)
        conflicts = self.conflict_detector.detect_conflicts(context.workspace_root, plan)

        return RefactoringPreview(
            plan=plan,
            diffs=[],
            conflicts=conflicts,
            estimated_risk=plan.estimated_risk,
            rollback_available=True,
        )
