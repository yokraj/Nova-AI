"""Windows Provider encapsulates Win32 UI handles and shell process discovery.
"""

from typing import Any
from app.ai.automation.window_manager import WindowManager
from app.ai.automation.process_manager import ProcessManager

class WindowsAutomationProvider:
    """Consolidates Windows-specific Win32 execution wrappers."""

    def __init__(self, parent_provider: Any = None) -> None:
        self.is_mock = False
        self.window = WindowManager(parent_provider)
        self.process = ProcessManager(parent_provider)
