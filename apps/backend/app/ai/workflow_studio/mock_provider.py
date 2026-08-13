"""Mock Workflow Studio Provider returning deterministic test responses for offline tests and CI.
"""

from typing import Any, Dict, List
from app.ai.workflow_studio.models import WorkflowDefinition, WorkflowExecutionResult, WorkflowStep


class MockWorkflowStudioProvider:
    """Mock Workflow Studio Provider returning deterministic test responses."""

    async def mock_record_workflow(self, name: str) -> WorkflowDefinition:
        return WorkflowDefinition(
            name=name,
            steps=[WorkflowStep(description="Mock Step")],
        )

    async def mock_play_workflow(self, workflow_id: str) -> WorkflowExecutionResult:
        return WorkflowExecutionResult(
            workflow_id=workflow_id,
            success=True,
            steps_completed=1,
            duration_sec=0.05,
        )
