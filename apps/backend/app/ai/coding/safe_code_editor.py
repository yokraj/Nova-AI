"""Safe Code Editing Engine for Nova-AI's Autonomous Coding Agent.

Executes atomic, verified file modifications with stale context detection,
pre-edit backup checkpointing, syntax validation, and clean diff generation.
Prevents silent overwrites of user external modifications.
"""

import os
import ast
import json
import hashlib
import difflib
import shutil
from typing import Any, Dict, Optional, Tuple
import structlog

from app.ai.desktop_automation.security_engine import SecurityEngine

logger = structlog.get_logger("safe_code_editor")


class StaleContextError(Exception):
    """Raised when target file was modified externally after observation."""
    pass


class SyntaxValidationError(Exception):
    """Raised when modified code fails language syntax validation."""
    pass


class SafeCodeEditor:
    """Atomic and safe code modification engine."""

    def __init__(self, backup_dir: Optional[str] = None) -> None:
        self.backup_dir = backup_dir or os.path.join(os.path.expanduser("~"), ".nova", "code_checkpoints")
        os.makedirs(self.backup_dir, exist_ok=True)
        self.security = SecurityEngine()
        self._observed_hashes: Dict[str, str] = {}

    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """Computes SHA-256 hash of target file content."""
        if not os.path.exists(file_path):
            return ""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            buf = f.read(65536)
            while buf:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    def record_observed_state(self, file_path: str) -> str:
        """Records current file hash as the baseline observed state."""
        abs_p = os.path.abspath(file_path)
        h = self.compute_file_hash(abs_p)
        self._observed_hashes[abs_p] = h
        return h

    def create_checkpoint(self, file_path: str) -> str:
        """Creates a timestamped backup copy of target file."""
        abs_p = os.path.abspath(file_path)
        if not os.path.exists(abs_p):
            return ""

        filename = os.path.basename(abs_p)
        backup_name = f"{filename}.bak_{hashlib.md5(abs_p.encode()).hexdigest()[:8]}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        shutil.copy2(abs_p, backup_path)
        logger.info("Created pre-edit backup checkpoint", original=abs_p, backup=backup_path)
        return backup_path

    def validate_syntax(self, file_path: str, new_content: str) -> bool:
        """Validates syntax of new content before committing to disk."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".py":
            try:
                ast.parse(new_content)
                return True
            except SyntaxError as e:
                raise SyntaxValidationError(f"Python syntax error in {file_path}: {e}")
        elif ext == ".json":
            try:
                json.loads(new_content)
                return True
            except json.JSONDecodeError as e:
                raise SyntaxValidationError(f"JSON format error in {file_path}: {e}")
        return True

    def apply_edit(
        self,
        file_path: str,
        new_content: str,
        expected_hash: Optional[str] = None,
        validate: bool = True,
    ) -> Dict[str, Any]:
        """Applies verified modification to target file atomically."""
        abs_p = os.path.abspath(file_path)

        # 1. Stale Context / External Conflict Check
        current_hash = self.compute_file_hash(abs_p)
        expected = expected_hash or self._observed_hashes.get(abs_p)

        if expected and current_hash and current_hash != expected:
            raise StaleContextError(
                f"File '{abs_p}' was modified externally after Nova observed it. "
                "Aborting edit to prevent destroying external user changes."
            )

        # 2. Syntax Validation
        if validate and os.path.exists(abs_p):
            self.validate_syntax(abs_p, new_content)

        # 3. Create Backup Checkpoint
        backup_p = self.create_checkpoint(abs_p) if os.path.exists(abs_p) else ""

        # 4. Read old content for diff generation
        old_content = ""
        if os.path.exists(abs_p):
            with open(abs_p, "r", encoding="utf-8", errors="ignore") as f:
                old_content = f.read()

        # 5. Write content atomically
        os.makedirs(os.path.dirname(abs_p), exist_ok=True)
        temp_p = f"{abs_p}.tmp_{os.getpid()}"
        with open(temp_p, "w", encoding="utf-8") as f:
            f.write(new_content)

        shutil.move(temp_p, abs_p)

        # 6. Generate Unified Diff
        diff_lines = list(
            difflib.unified_diff(
                old_content.splitlines(),
                new_content.splitlines(),
                fromfile=f"a/{os.path.basename(abs_p)}",
                tofile=f"b/{os.path.basename(abs_p)}",
                lineterm="",
            )
        )
        diff_str = "\n".join(diff_lines)

        # 7. Update observed hash
        new_hash = self.compute_file_hash(abs_p)
        self._observed_hashes[abs_p] = new_hash

        logger.info("Successfully applied safe code edit", file=abs_p, backup=backup_p)
        return {
            "file_path": abs_p,
            "success": True,
            "backup_path": backup_p,
            "diff": diff_str,
            "new_hash": new_hash,
        }
