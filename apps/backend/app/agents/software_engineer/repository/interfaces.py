"""Interface specifications outlining abstract boundaries for Repository components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.agents.software_engineer.repository.models import (
    DependencyInfo,
    RepositoryIndex,
    RepositoryNode,
    ScanResult,
)


class RepositoryScanner(ABC):
    """Abstract interface for repository file scanner."""

    @abstractmethod
    def scan(self, workspace_path: str, cache: Optional[Any] = None) -> List[Any]:
        """Scans workspace path returning file and directory information list."""
        pass


class RepositoryDetector(ABC):
    """Abstract interface for repository language, framework, and dependency detector."""

    @abstractmethod
    def detect_languages(self, file_path: str) -> Optional[str]:
        """Resolves file path to language string identifier."""
        pass

    @abstractmethod
    def detect_frameworks(self, workspace_path: str, files: List[str]) -> List[Any]:
        """Detects framework profiles from workspace file listings and manifests."""
        pass

    @abstractmethod
    def detect_dependencies(self, workspace_path: str, files: List[str]) -> List[DependencyInfo]:
        """Parses manifest files extracting dependency definitions lists."""
        pass


class RepositoryIndexer(ABC):
    """Abstract interface for indexing scanned files."""

    @abstractmethod
    def build_index(self, root_path: str, files: List[Any]) -> RepositoryIndex:
        """Builds lookup index models mapping filenames, locations, languages, and extensions."""
        pass


class RepositoryCache(ABC):
    """Abstract interface for saving and loading scan results between executions."""

    @abstractmethod
    def load(self) -> Optional[Any]:
        """Loads cached scan database metadata."""
        pass

    @abstractmethod
    def save(self, scan_duration: float = 0.0) -> None:
        """Persists current memory database cache changes."""
        pass

    @abstractmethod
    def invalidate(self) -> None:
        """Cleans and clears cached files."""
        pass

    @abstractmethod
    def reload(self) -> None:
        """Reloads cache metadata from filesystem."""
        pass

    @abstractmethod
    def get_entry(self, rel_path: str) -> Optional[Any]:
        """Fetches cache records for file relative path."""
        pass

    @abstractmethod
    def set_entry(self, rel_path: str, entry: Any) -> None:
        """Registers a file signature entry on cache registry."""
        pass


class RepositoryAnalyzer(ABC):
    """Main Orchestrator API abstraction interface for Repository Intelligence."""

    @abstractmethod
    def analyze(self, workspace_path: str) -> ScanResult:
        """Performs full workspace verification, scan, detections, and statistics analysis."""
        pass
