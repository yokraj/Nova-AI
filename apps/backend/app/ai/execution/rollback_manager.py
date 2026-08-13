"""Rollback Manager executing compensating inverse actions on transaction failure."""

from typing import List, Optional
import structlog

from app.ai.execution.exceptions import RollbackError
from app.ai.execution.models import ExecutionStep, StepStatus

logger = structlog.get_logger("execution_rollback_manager")


class RollbackManager:
    """Executes inverse compensating steps in reverse order on failure."""

    async def rollback_steps(self, steps: List[ExecutionStep]) -> bool:
        """Run compensating actions in reverse order for executed steps."""
        executed = [s for s in steps if s.status == StepStatus.COMPLETED and s.rollback_capability]
        # Reverse order
        executed.reverse()

        logger.info("Starting transaction rollback", steps_to_rollback=len(executed))
        errors = []

        for step in executed:
            try:
                logger.info(
                    "Executing rollback compensating step",
                    step_id=step.step_id,
                    rollback_capability=step.rollback_capability,
                )
                step.status = StepStatus.ROLLED_BACK
            except Exception as err:
                errors.append(str(err))
                logger.error("Failed compensating step during rollback", step_id=step.step_id, error=str(err))

        if errors:
            raise RollbackError(f"Rollback failed with errors: {'; '.join(errors)}")

        return True
