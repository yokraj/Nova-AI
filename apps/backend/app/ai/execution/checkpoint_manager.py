"""Checkpoint Manager serializing mission checkpoints to disk for interruption recovery."""

import json
import os
from typing import Any, Dict, Optional
import structlog

from app.ai.execution.configuration import ExecutionConfiguration
from app.ai.execution.interfaces import ICheckpointManager
from app.ai.execution.models import CheckpointData, ExecutionState, MissionExecutionPlan

logger = structlog.get_logger("execution_checkpoint_manager")


class CheckpointManager(ICheckpointManager):
    """Persists and restores mission execution checkpoints."""

    def __init__(self, config: Optional[ExecutionConfiguration] = None) -> None:
        self.config = config or ExecutionConfiguration()
        self.storage_dir = self.config.checkpoint_dir
        self._memory_checkpoints: Dict[str, CheckpointData] = {}
        self._ensure_dir()

    async def create_checkpoint(
        self,
        plan: MissionExecutionPlan,
        context_data: Dict[str, Any],
    ) -> CheckpointData:
        """Create and persist a checkpoint snapshot."""
        completed_ids = [s.step_id for s in plan.steps if s.status.value == "completed"]
        step_outputs = {s.step_id: s.output for s in plan.steps if s.output is not None}

        chk = CheckpointData(
            mission_id=plan.mission_id,
            goal=plan.goal,
            completed_step_ids=completed_ids,
            step_outputs=step_outputs,
            shared_context=context_data,
            state=ExecutionState.PAUSED if plan.state == ExecutionState.RUNNING else plan.state,
        )

        self._memory_checkpoints[plan.mission_id] = chk

        # Persist to JSON file
        try:
            file_path = os.path.join(self.storage_dir, f"{plan.mission_id}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(chk.model_dump_json(indent=2))
            logger.info("Saved mission checkpoint to disk", mission_id=plan.mission_id, path=file_path)
        except Exception as err:
            logger.warning("Failed to save checkpoint to disk", mission_id=plan.mission_id, error=str(err))

        return chk

    async def load_checkpoint(self, mission_id: str) -> Optional[CheckpointData]:
        """Load checkpoint snapshot by mission_id."""
        if mission_id in self._memory_checkpoints:
            return self._memory_checkpoints[mission_id]

        file_path = os.path.join(self.storage_dir, f"{mission_id}.json")
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = f.read()
            chk = CheckpointData.model_validate_json(raw)
            self._memory_checkpoints[mission_id] = chk
            logger.info("Loaded mission checkpoint from disk", mission_id=mission_id)
            return chk
        except Exception as err:
            logger.error("Failed to parse checkpoint file", mission_id=mission_id, error=str(err))
            return None

    def _ensure_dir(self) -> None:
        try:
            os.makedirs(self.storage_dir, exist_ok=True)
        except Exception:
            pass
