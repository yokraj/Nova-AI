"""Context Builder aggregates desktop states snapshots.
"""

import structlog
from typing import Dict, Any

logger = structlog.get_logger("context_builder")

class ContextBuilder:
    """Queries active window, processes, and clipboard sizes to compile snapshots."""

    def __init__(self, provider: Any) -> None:
        self.provider = provider

    def build_context(self) -> Dict[str, Any]:
        """Gathers system attributes into state dictionaries."""
        ctx: Dict[str, Any] = {
            "active_window": None,
            "processes_count": 0,
            "clipboard_size": 0,
        }

        # Query foreground window
        if hasattr(self.provider, "window"):
            active = self.provider.window.active_window()
            if active:
                ctx["active_window"] = active

        # Query processes
        if hasattr(self.provider, "process"):
            procs = self.provider.process.list_processes()
            ctx["processes_count"] = len(procs)

        # Query clipboard text sizes
        if hasattr(self.provider, "clipboard"):
            val = self.provider.clipboard.read()
            ctx["clipboard_size"] = len(val)

        return ctx
