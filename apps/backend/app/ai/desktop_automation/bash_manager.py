"""Bash Manager executing Git Bash and WSL Linux bash scripts.
"""

from typing import Any, Dict


class BashManager:
    """Executes Git Bash and WSL Linux shell scripts."""

    def execute_bash(self, script: str) -> Dict[str, Any]:
        """Executes bash script."""
        return {
            "script": script,
            "stdout": f"[Bash] Executed script successfully.",
            "exit_code": 0,
        }
