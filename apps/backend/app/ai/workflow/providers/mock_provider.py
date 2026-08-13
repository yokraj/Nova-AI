"""Mock provider simulating dynamic workflows execution logs offline.
"""

from typing import Dict, Any

class MockWorkflowProvider:
    """Simulates workflow steps transitions, rollbacks, and recovery checkpoints."""

    def simulate_sequential(self) -> Dict[str, Any]:
        """Simulates sequential design-build workflow lifecycle runs."""
        return {
            "workflow_id": "sequential_mock_wf",
            "steps_completed": ["step_arch", "step_api", "step_db"],
            "final_progress": 100.0,
            "state": "completed"
        }

    def simulate_parallel(self) -> Dict[str, Any]:
        """Simulates simultaneous execution of frontend and backend tasks."""
        return {
            "workflow_id": "parallel_mock_wf",
            "parallel_branches": {
                "branch_frontend": ["step_layout", "step_style"],
                "branch_backend": ["step_crud", "step_auth"]
            },
            "state": "completed"
        }

    def simulate_rollback(self) -> Dict[str, Any]:
        """Simulates failed section rollback triggers restoring previous state values."""
        return {
            "workflow_id": "rollback_mock_wf",
            "failed_step": "step_deploy",
            "rolled_back_steps": ["step_deploy", "step_compile"],
            "state": "pending"
        }
