"""Implements multi-key indexing and search lookups for repository files.
"""

import os
from typing import Dict, List
from app.agents.software_engineer.repository.interfaces import RepositoryIndexer
from app.agents.software_engineer.repository.models import DependencyInfo, FileInfo, RepositoryIndex


class ModelRepositoryIndexer(RepositoryIndexer):
    """Builds search indexes matching relative paths, extensions, directories and dependencies."""

    def build_index(self, root_path: str, files: List[FileInfo]) -> RepositoryIndex:
        """Constructs lookup tables for instantaneous file queries.

        Args:
            root_path: Root workspace folder path.
            files: List of scanned files.

        Returns:
            Built RepositoryIndex model containing mappings.
        """
        by_filename: Dict[str, List[str]] = {}
        by_extension: Dict[str, List[str]] = {}
        by_directory: Dict[str, List[str]] = {}
        by_language: Dict[str, List[str]] = {}
        by_framework: Dict[str, List[str]] = {}
        by_dependency: Dict[str, List[str]] = {}
        by_relative_path: Dict[str, str] = {}
        by_absolute_path: Dict[str, str] = {}

        for f in files:
            rel_path = f.relative_path
            abs_path = f.absolute_path

            by_relative_path[rel_path] = abs_path
            by_absolute_path[abs_path] = rel_path

            # Filename
            fname = os.path.basename(rel_path)
            by_filename.setdefault(fname, []).append(rel_path)

            # Extension
            ext = os.path.splitext(rel_path)[1].lower()
            if ext:
                by_extension.setdefault(ext, []).append(rel_path)

            # Directory
            dirname = os.path.dirname(rel_path)
            by_directory.setdefault(dirname, []).append(rel_path)

            # Language
            if f.language:
                by_language.setdefault(f.language, []).append(rel_path)

            # Framework
            if f.framework:
                by_framework.setdefault(f.framework, []).append(rel_path)

        return RepositoryIndex(
            by_filename=by_filename,
            by_extension=by_extension,
            by_directory=by_directory,
            by_language=by_language,
            by_framework=by_framework,
            by_dependency=by_dependency,
            by_relative_path=by_relative_path,
            by_absolute_path=by_absolute_path,
        )
