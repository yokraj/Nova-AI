"""Implements path validation and exclude filtering.
"""

import fnmatch
import os
from pathlib import Path
from typing import List, Optional, Set, Union

DEFAULT_IGNORE_PATTERNS = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
    "bin",
    "obj",
    "venv",
    ".venv",
    "coverage",
    ".pytest_cache",
    ".next",
    ".cache",
}


class PathFilter:
    """Filters workspace files and directories by config settings and defaults."""

    def __init__(
        self,
        ignore_patterns: Optional[Union[List[str], Set[str]]] = None,
        ignore_hidden: bool = True,
        max_file_size: Optional[int] = None,
        max_depth: Optional[int] = None,
    ) -> None:
        """Initializes PathFilter with configurable options.

        Args:
            ignore_patterns: Glob patterns of paths/files to ignore.
            ignore_hidden: If True, filters hidden files/directories starting with '.'.
            max_file_size: Maximum allowed file size in bytes.
            max_depth: Maximum recursion depth from workspace root.
        """
        self.ignore_patterns = (
            set(ignore_patterns) if ignore_patterns is not None else DEFAULT_IGNORE_PATTERNS
        )
        self.ignore_hidden = ignore_hidden
        self.max_file_size = max_file_size
        self.max_depth = max_depth

    def should_ignore(self, path: Union[str, Path], root_path: Union[str, Path]) -> bool:
        """Checks if a file path matches ignore lists or exceeds constraint limits.

        Args:
            path: Target file path.
            root_path: Workspace root directory path.

        Returns:
            True if path should be ignored, False otherwise.
        """
        p = Path(path)
        root = Path(root_path)
        try:
            rel_p = p.relative_to(root)
        except ValueError:
            rel_p = p

        # Max depth check
        if self.max_depth is not None and len(rel_p.parts) > self.max_depth:
            return True

        # Check part-by-part to handle recursive paths and direct patterns
        for part in rel_p.parts:
            # Skip checking root node placeholders
            if part in (".", ".."):
                continue

            # Hidden check
            if self.ignore_hidden and part.startswith(".") and part not in {".git", ".github", ".vscode", ".pytest_cache", ".next", ".cache"}:
                # Note: Default patterns like .git, etc. are handled by ignore_patterns
                # But any other hidden file/folder (e.g. .mypy_cache, .project_meta) is ignored if ignore_hidden is True.
                # Let's check against hidden files/directories generally:
                return True

            # If hidden checking is enabled, any component starting with "." gets ignored (except if explicitly allowed, but here we ignore all)
            if self.ignore_hidden and part.startswith(".") and part != ".":
                return True

            # Pattern check
            for pattern in self.ignore_patterns:
                if fnmatch.fnmatch(part, pattern):
                    return True

        # File size check
        if p.is_file() and self.max_file_size is not None:
            try:
                if p.stat().st_size > self.max_file_size:
                    return True
            except OSError:
                return True  # If unable to access file info, skip it.

        return False

    def should_ignore_dir(self, dir_path: Union[str, Path], root_path: Union[str, Path]) -> bool:
        """Determines if a directory can be completely skipped during traversal.

        Args:
            dir_path: Target directory path.
            root_path: Workspace root directory path.

        Returns:
            True if directory is ignored, False otherwise.
        """
        p = Path(dir_path)
        root = Path(root_path)
        try:
            rel_p = p.relative_to(root)
        except ValueError:
            rel_p = p

        # Max depth check
        if self.max_depth is not None and len(rel_p.parts) > self.max_depth:
            return True

        # Check path components
        for part in rel_p.parts:
            if part in (".", ".."):
                continue

            if self.ignore_hidden and part.startswith(".") and part != ".":
                return True

            for pattern in self.ignore_patterns:
                if fnmatch.fnmatch(part, pattern):
                    return True

        return False
