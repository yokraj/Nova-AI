"""Mock Execution Provider — deterministic offline simulations for testing and development."""

from typing import Any, Dict, List
from app.ai.execution.models import ExecutionState, ExecutionStep, MissionExecutionPlan, StepStatus


class MockExecutionProvider:
    """Provides deterministic, offline simulations of execution runtime operations."""

    def simulate_mission_plan(self, mission_id: str = "ms_mock_001") -> MissionExecutionPlan:
        """Return a pre-built mock execution plan."""
        return MissionExecutionPlan(
            mission_id=mission_id,
            goal="Summarize today's PDF and email to John",
            steps=[
                ExecutionStep(
                    step_id="step_1",
                    name="Summarize PDF",
                    plugin_id="pdf",
                    capability="summarize_pdf",
                    parameters={"path": "report.pdf"},
                    status=StepStatus.COMPLETED,
                    output="Summary: Q3 Revenue +15%",
                ),
                ExecutionStep(
                    step_id="step_2",
                    name="Send Email",
                    plugin_id="email",
                    capability="send_email",
                    parameters={"to": "john@example.com", "subject": "Summary"},
                    requires_approval=True,
                    status=StepStatus.COMPLETED,
                    output={"status": "sent"},
                ),
            ],
            state=ExecutionState.COMPLETED,
            progress_percentage=100.0,
        )

    @staticmethod
    def simulate_metrics() -> Dict[str, Any]:
        """Return a mock metrics dictionary snapshot."""
        return {
            "total_missions": 10,
            "completed_missions": 9,
            "failed_missions": 1,
            "cancelled_missions": 0,
            "success_rate": 0.90,
            "average_mission_duration_seconds": 12.5,
            "total_steps_executed": 24,
            "total_retries": 1,
            "total_rollbacks": 0,
            "human_approvals_requested": 3,
        }

    @staticmethod
    def simulate_health() -> Dict[str, Any]:
        """Return healthy status simulation dict."""
        return {
            "status": "healthy",
            "components": {
                "queue": "online",
                "checkpoint_manager": "online",
                "resource_manager": "online",
            },
            "active_missions_count": 0,
            "queued_tasks_count": 0,
        }
