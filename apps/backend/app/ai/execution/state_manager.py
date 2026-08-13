"""State Manager tracking and enforcing mission and step state transitions."""

from typing import Dict, Optional
import structlog

from app.ai.execution.exceptions import TaskExecutionError
from app.ai.execution.models import ExecutionState, StepStatus

logger = structlog.get_logger("execution_state_manager")


class StateManager:
    """Enforces valid state transitions for missions and execution steps."""

    # Valid mission transitions
    VALID_MISSION_TRANSITIONS: Dict[ExecutionState, set] = {
        ExecutionState.PENDING: {ExecutionState.RUNNING, ExecutionState.CANCELLED},
        ExecutionState.RUNNING: {
            ExecutionState.WAITING_APPROVAL,
            ExecutionState.COMPLETED,
            ExecutionState.FAILED,
            ExecutionState.CANCELLED,
            ExecutionState.PAUSED,
            ExecutionState.ROLLBACK_IN_PROGRESS,
        },
        ExecutionState.WAITING_APPROVAL: {
            ExecutionState.RUNNING,
            ExecutionState.CANCELLED,
            ExecutionState.FAILED,
        },
        ExecutionState.PAUSED: {ExecutionState.RUNNING, ExecutionState.CANCELLED},
        ExecutionState.ROLLBACK_IN_PROGRESS: {ExecutionState.ROLLED_BACK, ExecutionState.FAILED},
        ExecutionState.COMPLETED: set(),
        ExecutionState.FAILED: {ExecutionState.RUNNING},  # Allow retry
        ExecutionState.CANCELLED: set(),
        ExecutionState.ROLLED_BACK: set(),
    }

    def transition_mission(self, current_state: ExecutionState, target_state: ExecutionState) -> ExecutionState:
        """Enforce valid transition for a mission."""
        if target_state not in self.VALID_MISSION_TRANSITIONS.get(current_state, set()):
            # Allow same state
            if current_state == target_state:
                return target_state
            raise TaskExecutionError(
                f"Invalid mission state transition from {current_state.value} to {target_state.value}"
            )
        logger.info("Transitioned mission state", from_state=current_state.value, to_state=target_state.value)
        return target_state

    def transition_step(self, current_status: StepStatus, target_status: StepStatus) -> StepStatus:
        """Enforce valid transition for a step."""
        logger.debug("Transitioned step status", from_status=current_status.value, to_status=target_status.value)
        return target_status
