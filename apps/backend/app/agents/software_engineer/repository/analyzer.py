"""Main RepositoryAnalyzer orchestrator implementing scan workflows and legacy APIs.
"""

import os
import time
from typing import Any, Dict, List, Optional

# Import legacy interface to support backward compatibility
from app.agents.software_engineer.interfaces import IRepositoryAnalyzer as ILegacyRepositoryAnalyzer
from app.agents.software_engineer.repository.cache import CacheEntry, FileSystemRepositoryCache
from app.agents.software_engineer.repository.detector import ModelRepositoryDetector
from app.agents.software_engineer.repository.exceptions import (
    InvalidRepositoryError,
    RepositoryNotFoundError,
    RepositoryScanError,
)
from app.agents.software_engineer.repository.filters import PathFilter
from app.agents.software_engineer.repository.indexer import ModelRepositoryIndexer
from app.agents.software_engineer.repository.interfaces import (
    RepositoryAnalyzer as IRepositoryAnalyzer,
)
from app.agents.software_engineer.repository.metadata import generate_metadata
from app.agents.software_engineer.repository.models import RepositoryInfo, ScanResult
from app.agents.software_engineer.repository.scanner import FileSystemRepositoryScanner
from app.agents.software_engineer.repository.statistics import compute_statistics
from app.agents.software_engineer.repository.tree import build_repository_tree
from app.agents.software_engineer.repository.utils import detect_git_info


class RepositoryAnalyzer(IRepositoryAnalyzer, ILegacyRepositoryAnalyzer):
    """The central Repository intelligence API orchestrating scans and metrics compilation."""

    def __init__(
        self,
        workspace_root: Optional[str] = None,
        ignore_patterns: Optional[List[str]] = None,
        ignore_hidden: bool = True,
        max_file_size: Optional[int] = None,
        max_depth: Optional[int] = None,
    ) -> None:
        """Initializes RepositoryAnalyzer with settings.

        Args:
            workspace_root: Default root folder of workspace.
            ignore_patterns: Glob ignore patterns.
            ignore_hidden: If True, skip hidden files.
            max_file_size: Max allowed file size in bytes.
            max_depth: Max depth of folders to crawl.
        """
        self.workspace_root = workspace_root
        self.path_filter = PathFilter(
            ignore_patterns=ignore_patterns,
            ignore_hidden=ignore_hidden,
            max_file_size=max_file_size,
            max_depth=max_depth,
        )
        self.scanner = FileSystemRepositoryScanner(path_filter=self.path_filter)
        self.detector = ModelRepositoryDetector()
        self.indexer = ModelRepositoryIndexer()
        self.cache: Optional[FileSystemRepositoryCache] = None

    def _get_cache_path(self, workspace_path: str) -> str:
        """Determines default cache file path in workspace."""
        return os.path.join(workspace_path, ".nova", "repo_cache.json")

    def validate_workspace(self, workspace_path: str) -> None:
        """Validates that workspace directory is readable and exists.

        Args:
            workspace_path: Workspace directory path.

        Raises:
            RepositoryNotFoundError: If workspace path does not exist.
            InvalidRepositoryError: If workspace path is not readable or not a directory.
        """
        if not workspace_path:
            raise InvalidRepositoryError("Workspace path cannot be empty.")

        abs_path = os.path.abspath(workspace_path)
        if not os.path.exists(abs_path):
            raise RepositoryNotFoundError(f"Workspace path does not exist: {abs_path}")

        if not os.path.isdir(abs_path):
            raise InvalidRepositoryError(f"Workspace path is not a directory: {abs_path}")

        if not os.access(abs_path, os.R_OK):
            raise InvalidRepositoryError(f"Workspace path is not readable: {abs_path}")

    def analyze(self, workspace_path: str) -> ScanResult:
        """Runs full repository scanning and metadata aggregation.

        Args:
            workspace_path: Target workspace path to analyze.

        Returns:
            ScanResult model containing statistics, trees, indexes and Git metadata.
        """
        start_time = time.perf_counter()

        # 1. Validate Workspace
        self.validate_workspace(workspace_path)
        abs_workspace = os.path.abspath(workspace_path)

        # 2. Setup Cache
        cache_file = self._get_cache_path(abs_workspace)
        self.cache = FileSystemRepositoryCache(cache_file)

        # 3. File System Scanning (Leveraging Cache for Incremental updates)
        files = self.scanner.scan(abs_workspace, self.cache)

        # 4. Perform Language and Framework detection per scanned file
        for f in files:
            # If cache didn't provide language, detect it
            if not f.language:
                f.language = self.detector.detect_languages(f.absolute_path)

        # 5. Build Tree
        tree = build_repository_tree(abs_workspace, files)

        # 6. Aggregate Statistics
        stats = compute_statistics(abs_workspace, files)

        # 7. Compile Metadata (Frameworks, dependencies, git state)
        metadata = generate_metadata(abs_workspace, files, stats, self.detector)

        # 8. Build lookup Indexes
        index = self.indexer.build_index(abs_workspace, files)

        # Update by_dependency index based on dependencies detected in manifests
        for dep in metadata.dependencies:
            # Map dependency to the manifest files they are in
            manifest_files = []
            for f in files:
                fname = os.path.basename(f.relative_path)
                if fname in (
                    "requirements.txt",
                    "pyproject.toml",
                    "package.json",
                    "Cargo.toml",
                    "go.mod",
                    "pom.xml",
                    "build.gradle",
                ) or fname.endswith(".csproj"):
                    # Check if dependency matches this manifest manager
                    if (
                        (dep.manager == "pip" and fname in ("requirements.txt", "pyproject.toml"))
                        or (dep.manager == "poetry" and fname == "pyproject.toml")
                        or (dep.manager == "npm" and fname == "package.json")
                        or (dep.manager == "cargo" and fname == "Cargo.toml")
                        or (dep.manager == "go" and fname == "go.mod")
                        or (dep.manager == "maven" and fname == "pom.xml")
                        or (dep.manager == "nuget" and fname.endswith(".csproj"))
                    ):
                        manifest_files.append(f.relative_path)
            if manifest_files:
                index.by_dependency[dep.name] = manifest_files

        # 9. Update Cache with all current file details
        for f in files:
            self.cache.set_entry(
                f.relative_path,
                CacheEntry(
                    mtime=f.last_modified,
                    size=f.size,
                    sha256=f.sha256,
                    language=f.language,
                    framework=f.framework,
                ),
            )

        duration = time.perf_counter() - start_time
        self.cache.save(scan_duration=duration)

        repo_info = RepositoryInfo(root_path=abs_workspace, metadata=metadata, statistics=stats)

        return ScanResult(
            repository_info=repo_info,
            tree=tree,
            index=index,
            scan_duration=duration,
            scan_timestamp=time.time(),
        )

    # Legacy ILegacyRepositoryAnalyzer Methods
    def analyze_branches(self) -> List[str]:
        """Legacy API returning lists of branch names in active workspace.

        Returns:
            List of branch strings.
        """
        root = self.workspace_root or os.getcwd()
        git_info = detect_git_info(root)
        if git_info and git_info.branch:
            # Try to return all branches if git subprocess succeeds
            try:
                import subprocess

                res = subprocess.run(
                    ["git", "branch", "-a"],
                    cwd=git_info.repository_root,
                    capture_output=True,
                    text=True,
                )
                branches = []
                for line in res.stdout.splitlines():
                    branch_name = line.replace("*", "").strip()
                    if branch_name:
                        branches.append(branch_name)
                if branches:
                    return branches
            except Exception:
                pass
            return [git_info.branch]
        return ["main"]

    def get_commit_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Legacy API fetching git commit details list.

        Args:
            limit: Maximum count of commits to return.

        Returns:
            List of dictionary items containing commit metadata info.
        """
        root = self.workspace_root or os.getcwd()
        git_info = detect_git_info(root)
        commits = []
        if git_info:
            try:
                import subprocess

                res = subprocess.run(
                    ["git", "log", f"-n", str(limit), '--format=%H|%an|%ad|%s'],
                    cwd=git_info.repository_root,
                    capture_output=True,
                    text=True,
                )
                for line in res.stdout.splitlines():
                    parts = line.split("|", 3)
                    if len(parts) == 4:
                        commits.append(
                            {
                                "hash": parts[0],
                                "author": parts[1],
                                "date": parts[2],
                                "message": parts[3],
                            }
                        )
            except Exception:
                # Return placeholder if git subprocess command fails
                pass
        return commits
