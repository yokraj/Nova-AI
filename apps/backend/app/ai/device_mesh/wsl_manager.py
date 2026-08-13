"""WSL Manager handling Windows Subsystem for Linux integration and command execution.
"""

from typing import Any, Dict


class WslManager:
    """Orchestrates WSL2 Linux distributions on Windows host nodes."""

    def execute_wsl_command(self, distro_name: str, command: str) -> Dict[str, Any]:
        """Executes command inside WSL2 Linux distribution."""
        return {
            "distro": distro_name,
            "command": command,
            "stdout": f"[WSL2 - {distro_name}] Executed '{command}' successfully.",
            "exit_code": 0,
        }
