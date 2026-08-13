"""Resolves Python absolute and relative module imports to file paths.
"""

import os
from typing import List, Optional, Set, Tuple


class ImportResolver:
    """Resolves Python imports to relative or absolute filesystem file paths."""

    def __init__(self, workspace_path: str) -> None:
        self.workspace_path = os.path.abspath(workspace_path)
        # Search paths for absolute imports (typically workspace root)
        self.search_paths = [self.workspace_path]

    def resolve_import(self, module_name: str, current_file: str, level: int = 0) -> Optional[str]:
        """Resolves a module name to its file path on the filesystem.

        Args:
            module_name: Import module path (e.g. 'src.core.utils').
            current_file: File where import statement occurs.
            level: Level of relative import (0 for absolute, >=1 for relative).

        Returns:
            Resolved file path relative to workspace, or None.
        """
        # 1. Handle relative imports
        if level > 0:
            current_dir = os.path.dirname(os.path.abspath(current_file))
            # Move up the directory structure based on the level
            for _ in range(level - 1):
                current_dir = os.path.dirname(current_dir)

            # Map target module relative to this dir
            mod_parts = module_name.split(".") if module_name else []
            candidate_base = os.path.join(current_dir, *mod_parts)

            resolved = self._check_candidate(candidate_base)
            if resolved:
                return os.path.relpath(resolved, self.workspace_path)

            return None

        # 2. Handle absolute imports
        for search_path in self.search_paths:
            mod_parts = module_name.split(".")
            candidate_base = os.path.join(search_path, *mod_parts)

            resolved = self._check_candidate(candidate_base)
            if resolved:
                return os.path.relpath(resolved, self.workspace_path)

        return None

    def _check_candidate(self, base_path: str) -> Optional[str]:
        """Checks if a base path represents a module file or package folder.

        Args:
            base_path: Candidate folder path.

        Returns:
            Absolute file path if resolved, or None.
        """
        # Candidate 1: module file, e.g. path.py
        candidate_file = base_path + ".py"
        if os.path.exists(candidate_file) and os.path.isfile(candidate_file):
            return os.path.abspath(candidate_file)

        # Candidate 2: package dir, e.g. path/__init__.py
        candidate_init = os.path.join(base_path, "__init__.py")
        if os.path.exists(candidate_init) and os.path.isfile(candidate_init):
            return os.path.abspath(candidate_init)

        # Candidate 3: folder directory (for namespace packages)
        if os.path.exists(base_path) and os.path.isdir(base_path):
            return os.path.abspath(base_path)

        return None

    def get_module_name(self, file_path: str) -> str:
        """Converts file path back to Python dot-separated module name.

        Args:
            file_path: Relative or absolute file path.

        Returns:
            Module name (e.g. 'src.core.utils').
        """
        abs_path = os.path.abspath(file_path)
        for search_path in self.search_paths:
            if abs_path.startswith(search_path):
                rel = os.path.relpath(abs_path, search_path)
                base, _ = os.path.splitext(rel)
                parts = base.split(os.sep)
                if parts and parts[-1] == "__init__":
                    parts.pop()
                return ".".join(parts).replace("/", ".")
        # Fallback
        base, _ = os.path.splitext(os.path.basename(file_path))
        return base
