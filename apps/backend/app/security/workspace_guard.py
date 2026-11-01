"""Workspace Security Guard for Nova AI File & Document Intelligence.

Enforces workspace boundary sandboxing:
- Restricts all file system access to explicitly authorized workspace roots (default: C:\\Projects\\Nova-AI).
- Prevents path traversal (e.g. '../', '..\\', symlink escapes, null bytes).
- Validates file extensions, size limits (max 15MB), and readability.
- Rejects unauthorized absolute paths outside the workspace.
- Detects file references inside user prompts for grounded document inspection.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Set, Union
import structlog

logger = structlog.get_logger("workspace_guard")

# Authoritative Workspace Root: C:\Projects\Nova-AI
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent  # apps/backend
WORKSPACE_ROOT = BACKEND_DIR.parent.parent.resolve()  # C:\Projects\Nova-AI

# Max file size: 15 MB
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024

# Supported readable extensions
ALLOWED_DOCUMENT_EXTENSIONS: Set[str] = {
    ".txt", ".md", ".markdown", ".py", ".json", ".csv",
    ".pdf", ".docx", ".toml", ".yaml", ".yml",
    ".ts", ".js", ".tsx", ".jsx", ".html", ".css",
    ".sh", ".ps1", ".bat", ".sql", ".log", ".env.example"
}


class WorkspaceSecurityException(PermissionError):
    """Raised when an unauthorized path traversal or external filesystem access is attempted."""
    pass


class WorkspaceSecurityGuard:
    """Security validator guaranteeing zero unauthorized file access outside workspace roots."""

    def __init__(self, root_dir: Optional[Path] = None, max_size_bytes: int = MAX_FILE_SIZE_BYTES):
        self.root_dir = (root_dir or WORKSPACE_ROOT).resolve()
        self.max_size_bytes = max_size_bytes

    def is_path_safe(self, path_str: Union[str, Path]) -> bool:
        """Checks whether a target path resolves safely inside the authorized workspace root."""
        try:
            self.resolve_workspace_path(path_str)
            return True
        except (WorkspaceSecurityException, ValueError):
            return False

    def resolve_workspace_path(self, path_str: Union[str, Path]) -> Path:
        """Resolves target path against authorized workspace root, strictly enforcing sandbox boundaries.

        Args:
            path_str: Relative or absolute path string or Path object.

        Returns:
            Resolved canonical Path object strictly within workspace root.

        Raises:
            WorkspaceSecurityException: If target path escapes workspace boundary.
            ValueError: If path contains null bytes or illegal characters.
        """
        if not path_str:
            raise ValueError("Target path cannot be empty.")

        raw_str = str(path_str).strip().strip("'\"`")
        if "\0" in raw_str:
            raise ValueError("Null byte injection detected in path string.")

        target = Path(raw_str)

        # Handle absolute vs relative resolution
        if target.is_absolute():
            resolved = target.resolve()
        else:
            resolved = (self.root_dir / target).resolve()

        # Enforce boundary containment
        try:
            resolved.relative_to(self.root_dir)
        except ValueError:
            logger.warning(
                "unauthorized_path_traversal_blocked",
                raw_path=raw_str,
                resolved_path=str(resolved),
                workspace_root=str(self.root_dir),
            )
            raise WorkspaceSecurityException(
                f"Access Denied: Path '{raw_str}' resolves outside authorized workspace root '{self.root_dir}'."
            )

        return resolved

    def validate_file_access(self, resolved_path: Path) -> None:
        """Validates that a resolved file exists, is regular file, within size limits, and has allowed extension.

        Args:
            resolved_path: Canonical Path resolved via resolve_workspace_path.

        Raises:
            FileNotFoundError: If the target file does not exist.
            ValueError: If target is a directory, exceeds size limit, or unsupported extension.
        """
        if not resolved_path.exists():
            raise FileNotFoundError(f"File not found: '{resolved_path.name}' at path '{resolved_path}'")

        if not resolved_path.is_file():
            raise ValueError(f"Target is a directory or special device, not a regular file: '{resolved_path}'")

        file_size = resolved_path.stat().st_size
        if file_size > self.max_size_bytes:
            raise ValueError(
                f"File '{resolved_path.name}' ({file_size} bytes) exceeds maximum security limit of {self.max_size_bytes} bytes."
            )

        suffix = resolved_path.suffix.lower()
        if suffix not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format '{suffix}' for document intelligence. Allowed formats: {sorted(list(ALLOWED_DOCUMENT_EXTENSIONS))}"
            )

    def extract_file_references(self, prompt: str) -> List[str]:
        """Detects referenced file paths or filenames in a natural language user prompt.

        Matches:
        - Quoted paths: "path/to/file.ext" or 'README.md'
        - Explicit extensions: README.md, main.py, data.csv, report.pdf, doc.docx
        - Relative path indicators: ./file.ext, apps/backend/pyproject.toml

        Returns:
            List of unique detected file candidate strings in order of occurrence.
        """
        candidates: List[str] = []
        p = prompt.strip()

        # 1. Quoted paths
        quoted_pattern = r"[\"']([^\"']+\.[a-zA-Z0-9]{1,10})[\"']"
        for m in re.finditer(quoted_pattern, p):
            cand = m.group(1).strip()
            if cand and cand not in candidates:
                candidates.append(cand)

        # 2. Paths with Windows drive letter (e.g. C:/Windows/win.ini, C:\temp\file.txt)
        drive_pattern = r"[a-zA-Z]:[\\\/][\w\.\-\\\/]+"
        for m in re.finditer(drive_pattern, p):
            cand = m.group(0).strip(".,;:?!'\"")
            if cand and cand not in candidates:
                candidates.append(cand)

        # 3. Path traversal patterns (e.g. ../../secret.txt, ..\..\passwords.txt)
        traversal_pattern = r"(?:\.\.[\/\\])+[\w\.\-\\\/]+"
        for m in re.finditer(traversal_pattern, p):
            cand = m.group(0).strip(".,;:?!'\"")
            if cand and cand not in candidates:
                candidates.append(cand)

        # 4. Unquoted tokens with known extensions or path separators
        ext_pattern = r"(?:[\w\.\-\/\\]+\.(?:md|markdown|txt|py|json|csv|pdf|docx|toml|yaml|yml|ts|js|tsx|jsx|html|css|sh|ps1|bat|sql|log|ini|cfg|conf|exe|dll))"
        for m in re.finditer(ext_pattern, p, re.IGNORECASE):
            cand = m.group(0).strip(".,;:?!'\"")
            if cand and cand not in candidates:
                candidates.append(cand)

        return candidates
