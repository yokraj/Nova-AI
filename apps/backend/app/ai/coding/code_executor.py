"""Local Code Execution & Git Safety Engine for Nova-AI's Autonomous Coding Agent.

Executes local development validation commands (python, node, pytest, npm, git status, git diff),
enforces Git safety rules, secret redaction, and security gating.
"""

import os
import re
import time
import subprocess
from typing import Any, Dict, List, Optional
import structlog

from app.ai.desktop_automation.security_engine import SecurityEngine

logger = structlog.get_logger("code_executor")


class CodeExecutor:
    """Safe local command and toolchain execution engine."""

    DESTRUCTIVE_GIT_PATTERNS = [
        r"git\s+reset\s+--hard",
        r"git\s+clean\s+-f",
        r"git\s+push\s+.*--force",
        r"git\s+commit",
        r"git\s+branch\s+-D",
        r"git\s+checkout\s+--\s+\.",
    ]

    SECRET_PATTERNS = [
        (r"(?i)(api_key|apikey|secret|password|passwd|auth_token|access_token|private_key)\s*=\s*['\"]?[^\s'\"]+['\"]?", r"\1=[REDACTED_API_KEY]"),
        (r"(?i)bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*", r"Bearer [REDACTED_TOKEN]"),
        (r"ghp_[a-zA-Z0-9]{36}", r"[REDACTED_GITHUB_TOKEN]"),
        (r"sk-[a-zA-Z0-9_\-]{16,}", r"[REDACTED_API_KEY]"),
    ]

    def __init__(self, root_dir: str = ".") -> None:
        self.root_dir = os.path.abspath(root_dir)
        self.security = SecurityEngine()

    def redact_secrets(self, text: str) -> str:
        """Redacts sensitive credentials, passwords, and tokens from command output."""
        sanitized = text
        for pattern, replacement in self.SECRET_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized

    def is_destructive_git_command(self, cmd_str: str) -> bool:
        """Checks if Git command attempts destructive changes or automated commits."""
        for pattern in self.DESTRUCTIVE_GIT_PATTERNS:
            if re.search(pattern, cmd_str, re.IGNORECASE):
                return True
        return False

    def execute_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout_sec: float = 30.0,
        is_user_approved: bool = False,
    ) -> Dict[str, Any]:
        """Executes a local shell command securely with output capture and secret redaction."""
        target_dir = os.path.abspath(cwd or self.root_dir)

        # 1. Git Safety Check
        if self.is_destructive_git_command(command) and not is_user_approved:
            logger.warning("Blocked destructive Git command requiring explicit approval", command=command)
            return {
                "command": command,
                "returncode": 126,
                "stdout": "",
                "stderr": f"SECURITY BLOCK: Command '{command}' requires explicit human approval.",
                "duration_sec": 0.0,
                "success": False,
                "requires_human": True,
            }

        start_t = time.time()
        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=target_dir,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )
            duration = round(time.time() - start_t, 2)
            stdout = self.redact_secrets(res.stdout or "")
            stderr = self.redact_secrets(res.stderr or "")

            success = res.returncode == 0
            logger.info("Executed code command", command=command, returncode=res.returncode, duration=duration)
            return {
                "command": command,
                "returncode": res.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "duration_sec": duration,
                "success": success,
                "requires_human": False,
            }
        except subprocess.TimeoutExpired:
            duration = round(time.time() - start_t, 2)
            return {
                "command": command,
                "returncode": 124,
                "stdout": "",
                "stderr": f"Command '{command}' timed out after {timeout_sec} seconds.",
                "duration_sec": duration,
                "success": False,
                "requires_human": False,
            }
        except Exception as e:
            duration = round(time.time() - start_t, 2)
            return {
                "command": command,
                "returncode": 1,
                "stdout": "",
                "stderr": str(e),
                "duration_sec": duration,
                "success": False,
                "requires_human": False,
            }
