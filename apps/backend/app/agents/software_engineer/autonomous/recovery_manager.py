"""Recovery Manager manages task recovery options and rollback plans.
"""

from app.agents.software_engineer.autonomous.interfaces import IRecoveryManager
from app.agents.software_engineer.autonomous.models import RecoveryPlan, TaskExecution

class LocalRecoveryManager(IRecoveryManager):
    """Orchestrates pipeline rollbacks on failed steps."""

    def build_recovery_plan(self, failed_task: TaskExecution) -> RecoveryPlan:
        """Returns alternative actions based on failure details."""
        step_id = failed_task.step_id
        
        # Build specific recovery strategy based on step type
        if "generation" in step_id:
            # Try to run alternative generator or repair
            return RecoveryPlan(
                original_step_id=step_id,
                action="alternative",
                steps_to_execute=["step-debugging", "step-testing"]
            )
        elif "testing" in step_id:
            # Try to retry
            return RecoveryPlan(
                original_step_id=step_id,
                action="retry",
                steps_to_execute=[step_id]
            )
        else:
            # Rollback deployment/configs
            return RecoveryPlan(
                original_step_id=step_id,
                action="rollback",
                steps_to_execute=[]
            )
