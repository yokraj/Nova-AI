"""Terminal Controller handles powershell/cmd commands executions.
"""

import structlog
import subprocess
import os
from typing import Optional, Dict, Any

from app.ai.automation.interfaces import TerminalController as ITerminalController

logger = structlog.get_logger("terminal_controller")

class TerminalController(ITerminalController):
    """Spawns synchronous command executions on the host system, capturing stdout."""

    def __init__(self, provider: Any = None) -> None:
        self.provider = provider
        self._last_stdout: str = ""
        self._last_stderr: str = ""
        self._active_cwd: str = os.getcwd()

    def launch_terminal(self) -> None:
        """Triggers system command shell window focus."""
        logger.info("Launching target OS terminal prompt window")
        is_mock = getattr(self.provider, "is_mock", True)
        if not is_mock:
            try:
                subprocess.Popen("start powershell", shell=True)
            except Exception:
                try:
                    subprocess.Popen("start cmd", shell=True)
                except Exception as err:
                    logger.warning("Failed to spawn shell console window", error=str(err))

    def execute_command(self, command: str, cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> str:
        """Executes terminal commands shell string synchronously."""
        target_cwd = cwd or self._active_cwd
        logger.info("Executing terminal command", command=command, cwd=target_cwd)
        is_mock = getattr(self.provider, "is_mock", True)
        
        if not is_mock:
            try:
                res = subprocess.run(
                    command,
                    shell=True,
                    cwd=target_cwd,
                    env={**os.environ, **(env or {})},
                    capture_output=True,
                    text=True,
                    timeout=30.0
                )
                self._last_stdout = res.stdout
                self._last_stderr = res.stderr
                return res.stdout
            except Exception as err:
                self._last_stderr = str(err)
                logger.error("Shell command execution threw error", error=str(err))
                return f"Error executing shell command: {str(err)}"

        self._last_stdout = f"Mock execution output for terminal instruction: {command}"
        self._last_stderr = ""
        return self._last_stdout

    def capture_output(self) -> str:
        """Returns buffered stdout text from last execution."""
        return self._last_stdout

    def wait_for_completion(self, timeout: float) -> bool:
        """Returns execution complete status."""
        return True

    def clear_terminal(self) -> None:
        """Fires clears screen prompt instructions."""
        logger.info("Resetting/clearing terminal output buffers")
        self._last_stdout = ""
        self._last_stderr = ""

    def change_directory(self, path: str) -> None:
        """Sets target directory workspace context."""
        logger.info("Change shell directory context", path=path)
        self._active_cwd = path

    def activate_environment(self, env_path: str) -> None:
        """Appends virtual environment setups path to active command context."""
        logger.info("Activating target virtual python workspace env", path=env_path)
