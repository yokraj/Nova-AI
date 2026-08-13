"""Macro Engine implements recording, replaying, and JSON serialization of actions.
"""

import structlog
import time
from typing import Optional, Any

from app.ai.automation.interfaces import MacroRecorder as IMacroRecorder
from app.ai.automation.models import ActionSequence, ActionStep

logger = structlog.get_logger("macro_engine")

class MacroEngine(IMacroRecorder):
    """Traces mouse/keyboard operations and handles deterministic playback."""

    def __init__(self, executor: Optional[Any] = None) -> None:
        self.executor = executor
        self._is_recording = False
        self._recorded_steps: list[ActionStep] = []
        self._start_time = 0.0

    def start_recording(self) -> None:
        """Starts recording keyboard/mouse steps."""
        logger.info("Starting macro recording")
        self._is_recording = True
        self._recorded_steps = []
        self._start_time = time.time()

    def record_step(self, step: ActionStep) -> None:
        """Appends step to macro logs if active."""
        if self._is_recording:
            self._recorded_steps.append(step)
            self._start_time = time.time()

    def stop_recording(self) -> ActionSequence:
        """Stops recording and returns the compiled sequence."""
        logger.info("Stopping macro recording", steps_count=len(self._recorded_steps))
        self._is_recording = False
        return ActionSequence(steps=self._recorded_steps)

    async def play_macro(self, sequence: ActionSequence) -> bool:
        """Replays recorded sequence step by step."""
        if not self.executor:
            logger.warning("No executor configured for macro playback")
            return False

        logger.info("Starting macro playback", sequence_id=sequence.sequence_id, steps_count=len(sequence.steps))
        from app.ai.automation.execution_context import ExecutionContext
        ctx = ExecutionContext()
        
        for step in sequence.steps:
            try:
                await self.executor.execute_step(step, ctx)
            except Exception as err:
                logger.error("Playback failed at step", step_id=step.step_id, error=str(err))
                return False
        return True

    def export_macro(self, sequence: ActionSequence) -> str:
        """Serializes macro sequence to JSON format."""
        return sequence.model_dump_json(indent=2)

    def import_macro(self, json_str: str) -> ActionSequence:
        """Restores macro sequence from JSON format."""
        return ActionSequence.model_validate_json(json_str)
