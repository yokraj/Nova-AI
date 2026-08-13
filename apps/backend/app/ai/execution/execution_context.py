"""Execution Context sharing data across steps and plugins without recomputing."""

from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger("execution_context")


class ExecutionContext:
    """Thread-safe context store holding step outputs and shared state across a mission."""

    def __init__(self, mission_id: str, initial_data: Optional[Dict[str, Any]] = None) -> None:
        self.mission_id = mission_id
        self._data: Dict[str, Any] = initial_data or {}
        self._step_outputs: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Store shared context key-value pair."""
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve shared context value."""
        return self._data.get(key, default)

    def record_step_output(self, step_id: str, output: Any) -> None:
        """Record the output of an executed step."""
        self._step_outputs[step_id] = output
        logger.debug("Recorded step output in context", mission_id=self.mission_id, step_id=step_id)

    def get_step_output(self, step_id: str) -> Any:
        """Get output from a previously executed step."""
        return self._step_outputs.get(step_id)

    def get_all_outputs(self) -> Dict[str, Any]:
        """Get dict of all step outputs."""
        return dict(self._step_outputs)

    def dump_data(self) -> Dict[str, Any]:
        """Dump entire context dict for serialization."""
        return {
            "shared": dict(self._data),
            "step_outputs": dict(self._step_outputs),
        }

    def restore_data(self, data: Dict[str, Any]) -> None:
        """Restore context from serialized dict."""
        self._data = dict(data.get("shared", {}))
        self._step_outputs = dict(data.get("step_outputs", {}))
