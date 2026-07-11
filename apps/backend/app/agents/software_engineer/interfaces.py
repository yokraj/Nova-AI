"""Interfaces outlining abstractions for workspace, memory, and repository analysis.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IWorkspaceManager(ABC):
    """Abstract interface for workspace operations."""

    @abstractmethod
    def open_workspace(self, path: str) -> None:
        pass

    @abstractmethod
    def close_workspace(self) -> None:
        pass

    @abstractmethod
    def current_workspace(self) -> Optional[str]:
        pass

    @abstractmethod
    def list_files(self) -> List[str]:
        pass

    @abstractmethod
    def workspace_information(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def validate_workspace(self) -> bool:
        pass


class ISimplifiedMemory(ABC):
    """Abstract interface for agent memory logs tracking."""

    @abstractmethod
    def add_file(self, file_path: str) -> None:
        pass

    @abstractmethod
    def add_symbol(self, symbol_name: str) -> None:
        pass

    @abstractmethod
    def add_error(self, error_msg: str) -> None:
        pass

    @abstractmethod
    def add_task(self, task_id: str) -> None:
        pass

    @abstractmethod
    def add_search(self, query: str) -> None:
        pass


class IRepositoryAnalyzer(ABC):
    """Abstract interface for future repository intelligence integrations."""

    @abstractmethod
    def analyze_branches(self) -> List[str]:
        pass

    @abstractmethod
    def get_commit_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        pass


class ICodeIntelligence(ABC):
    """Abstract interface for future AST and code generation services."""

    @abstractmethod
    def find_definitions(self, file_path: str, symbol_name: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def find_references(self, file_path: str, symbol_name: str) -> List[Dict[str, Any]]:
        pass
