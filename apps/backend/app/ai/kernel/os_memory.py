"""OS Memory store maintaining running state, reasoning scratchpad, and execution stack.
"""

from typing import Any, Dict, List
from app.ai.kernel.interfaces import IOSMemory
from app.ai.kernel.models import OSMemoryState


class OSMemory(IOSMemory):
    """In-memory state store for AI OS Kernel execution runtime."""

    def __init__(self) -> None:
        self._state = OSMemoryState(
            current_tasks=[],
            active_goals=[],
            background_jobs=[],
            recent_actions=[],
            temporary_reasoning=[],
            execution_stack=[],
        )

    async def record_action(self, action_type: str, details: Dict[str, Any]) -> None:
        """Records an action in the audit trail.

        Args:
            action_type: Category of action.
            details: Contextual details.
        """
        record = {"action_type": action_type, "details": details}
        self._state.recent_actions.append(record)
        if len(self._state.recent_actions) > 100:
            self._state.recent_actions.pop(0)

    async def push_task(self, task: Dict[str, Any]) -> None:
        """Pushes a task into current task list."""
        self._state.current_tasks.append(task)

    async def push_reasoning(self, note: str) -> None:
        """Appends reasoning note to scratchpad."""
        self._state.temporary_reasoning.append(note)

    async def push_execution_stack(self, node_title: str) -> None:
        """Pushes step onto execution stack."""
        self._state.execution_stack.append(node_title)

    async def pop_execution_stack(self) -> str:
        """Pops top element off execution stack."""
        if self._state.execution_stack:
            return self._state.execution_stack.pop()
        return ""

    async def get_state(self) -> OSMemoryState:
        """Returns current OSMemoryState."""
        return self._state
