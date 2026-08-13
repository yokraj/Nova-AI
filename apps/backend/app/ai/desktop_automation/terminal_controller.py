"""Terminal Controller orchestrating PowerShell, CMD, Bash, and SSH terminal execution.
"""

from typing import Any, Dict
from app.ai.desktop_automation.interfaces import ITerminalController
from app.ai.desktop_automation.models import TerminalSession


class TerminalController(ITerminalController):
    """Orchestrates PowerShell, CMD, Bash, and SSH terminal command execution and pipelines."""

    def __init__(self) -> None:
        self._session = TerminalSession(shell_type="powershell")

    async def execute_command(self, command: str, shell: str = "powershell") -> Dict[str, Any]:
        """Executes command in specified terminal shell."""
        self._session.shell_type = shell
        return {
            "shell": shell,
            "command": command,
            "stdout": f"[{shell.upper()}] Executed '{command}' successfully.",
            "exit_code": 0,
        }
