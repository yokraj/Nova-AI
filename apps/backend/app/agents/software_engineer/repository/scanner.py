"""Implements high-performance workspace filesystem scanning.
"""

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.agents.software_engineer.repository.exceptions import RepositoryScanError
from app.agents.software_engineer.repository.filters import PathFilter
from app.agents.software_engineer.repository.interfaces import RepositoryScanner
from app.agents.software_engineer.repository.models import FileInfo


class FileSystemRepositoryScanner(RepositoryScanner):
    """Recursively scans repository workspaces, skipping ignored directories and files."""

    def __init__(
        self,
        path_filter: Optional[PathFilter] = None,
        follow_symlinks: bool = False,
        use_parallel: bool = True,
    ) -> None:
        """Initializes scanner settings.

        Args:
            path_filter: Exclude filter configurations.
            follow_symlinks: If True, resolve symlinks safely.
            use_parallel: If True, runs parallel stat lookups on files.
        """
        self.path_filter = path_filter or PathFilter()
        self.follow_symlinks = follow_symlinks
        self.use_parallel = use_parallel
        self._visited_symlinks = set()

    def scan(self, workspace_path: str, cache: Optional[Any] = None) -> List[FileInfo]:
        """Scans workspace path recursively returning files lists.

        Args:
            workspace_path: Target directory path to scan.
            cache: Cache interface for incremental lookups.

        Returns:
            List of FileInfo objects describing scanned files.

        Raises:
            RepositoryScanError: If scanning process fails.
        """
        abs_workspace = os.path.abspath(workspace_path)
        if not os.path.exists(abs_workspace):
            raise RepositoryScanError(f"Workspace path does not exist: {abs_workspace}")

        self._visited_symlinks.clear()
        files_to_stat = []

        try:
            self._walk_directory(abs_workspace, abs_workspace, files_to_stat)
        except Exception as e:
            raise RepositoryScanError(f"Failed during workspace file walk: {str(e)}") from e

        # Resolve stats (potentially in parallel)
        file_infos = []
        if self.use_parallel and len(files_to_stat) > 10:
            with ThreadPoolExecutor() as executor:
                # Map inputs
                futures = [
                    executor.submit(self._stat_file_info, f_path, abs_workspace, cache)
                    for f_path in files_to_stat
                ]
                for fut in futures:
                    info = fut.result()
                    if info:
                        file_infos.append(info)
        else:
            for f_path in files_to_stat:
                info = self._stat_file_info(f_path, abs_workspace, cache)
                if info:
                    file_infos.append(info)

        return file_infos

    def _walk_directory(self, current_dir: str, root_path: str, files_to_stat: List[str]) -> None:
        """Helper walking the filesystem, pruning early when directories are ignored."""
        try:
            entries = os.scandir(current_dir)
        except (PermissionError, FileNotFoundError):
            return

        for entry in entries:
            try:
                # Symlinks loop protection
                if entry.is_symlink():
                    if not self.follow_symlinks:
                        continue
                    real_path = os.path.realpath(entry.path)
                    if real_path in self._visited_symlinks:
                        continue
                    self._visited_symlinks.add(real_path)

                if entry.is_dir(follow_symlinks=self.follow_symlinks):
                    if not self.path_filter.should_ignore_dir(entry.path, root_path):
                        self._walk_directory(entry.path, root_path, files_to_stat)
                elif entry.is_file(follow_symlinks=self.follow_symlinks):
                    if not self.path_filter.should_ignore(entry.path, root_path):
                        files_to_stat.append(entry.path)
            except (PermissionError, FileNotFoundError):
                continue

    def _stat_file_info(
        self, file_path: str, root_path: str, cache: Optional[Any] = None
    ) -> Optional[FileInfo]:
        """Loads filesystem details, checking cache hits to save processing time."""
        try:
            rel_path = os.path.relpath(file_path, root_path)
            stat = os.stat(file_path)
            size = stat.st_size
            mtime = stat.st_mtime

            # Try to lookup cache
            if cache:
                cached_entry = cache.get_entry(rel_path)
                if cached_entry and cached_entry.mtime == mtime and cached_entry.size == size:
                    # Cache hit! Reuse details.
                    return FileInfo(
                        absolute_path=file_path,
                        relative_path=rel_path,
                        size=size,
                        last_modified=mtime,
                        sha256=cached_entry.sha256,
                        language=cached_entry.language,
                        framework=cached_entry.framework,
                    )

            # Fresh build
            return FileInfo(
                absolute_path=file_path,
                relative_path=rel_path,
                size=size,
                last_modified=mtime,
                sha256=None,  # Handled on analyzer if checksums are requested
                language=None,
                framework=None,
            )
        except (PermissionError, FileNotFoundError):
            return None
