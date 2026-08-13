"""Context Engine merging conversation, memory, desktop, browser, app, clipboard, calendar, mission, and project.
"""

from typing import Any, Dict, List, Optional
from app.ai.kernel.interfaces import IContextEngine
from app.ai.kernel.models import ExecutionContext


class ContextEngine(IContextEngine):
    """Context Engine producing unified OS context snapshot across subsystems."""

    def __init__(self) -> None:
        self._current_context = ExecutionContext(
            session_id="sess_default",
            conversation_history=[
                {"role": "system", "content": "Nova AI OS Kernel active."}
            ],
            memory_records=[
                {"key": "user_name", "value": "User"},
                {"key": "os_environment", "value": "Windows 11 Local-First"}
            ],
            desktop_context={"focused_window": "VSCode", "resolution": "1920x1080"},
            browser_state={"active_tab": "GitHub - Nova-AI", "url": "https://github.com/nova-ai"},
            active_application="VSCode",
            clipboard="npm test",
            calendar_events=[
                {"title": "System Checkup", "time": "14:00"}
            ],
            current_mission="msn_kernel_01",
            current_project="c:\\Projects\\Nova-AI",
        )

    async def get_unified_context(self, session_id: str = "sess_default") -> ExecutionContext:
        """Returns the current unified OS context.

        Args:
            session_id: Active session ID.

        Returns:
            ExecutionContext model instance.
        """
        self._current_context.session_id = session_id
        return self._current_context

    async def update_context(self, updates: Dict[str, Any]) -> ExecutionContext:
        """Updates fields in active unified context.

        Args:
            updates: Dictionary of fields to update.

        Returns:
            Updated ExecutionContext instance.
        """
        for key, val in updates.items():
            if hasattr(self._current_context, key):
                setattr(self._current_context, key, val)
        return self._current_context
