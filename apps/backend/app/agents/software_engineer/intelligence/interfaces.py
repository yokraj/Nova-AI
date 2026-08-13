"""Interfaces outlining abstractions for Code Intelligence services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.agents.software_engineer.intelligence.models import (
    AnalysisResult,
    CallGraph,
    ComplexityReport,
    DeadCodeReport,
    DependencyGraph,
    DuplicateReport,
    IntelligenceReport,
    RepositoryIntelligenceSummary,
    SemanticSearchResult,
    Symbol,
)


class ASTParser(ABC):
    """Abstract interface for parsing source files into structured AST info."""

    @abstractmethod
    def parse_file(self, file_path: str, root_path: str) -> Dict[str, Any]:
        """Parses a file and extracts raw symbols, imports, and expressions."""
        pass


class SymbolIndexer(ABC):
    """Abstract interface for maintaining symbol search indexes."""

    @abstractmethod
    def index_symbols(self, file_path: str, symbols: List[Symbol]) -> None:
        """Indexes symbols for the given file."""
        pass

    @abstractmethod
    def lookup_symbol(self, qualified_name: str) -> Optional[Symbol]:
        """Lookups symbol by its qualified name."""
        pass

    @abstractmethod
    def list_symbols(self) -> List[Symbol]:
        """Lists all indexed symbols."""
        pass


class DependencyAnalyzer(ABC):
    """Abstract interface for constructing imports dependency graphs."""

    @abstractmethod
    def analyze_dependencies(self, workspace_path: str, file_imports: Dict[str, List[Any]]) -> DependencyGraph:
        """Builds dependency relationship graph from extracted imports mapping."""
        pass


class ComplexityAnalyzer(ABC):
    """Abstract interface for cyclomatic and cognitive complexity metrics calculation."""

    @abstractmethod
    def calculate_complexity(self, file_path: str, source_code: str) -> ComplexityReport:
        """Calculates complexity reports for the given source code."""
        pass


class DuplicateAnalyzer(ABC):
    """Abstract interface for detecting duplicated code expressions using AST comparison."""

    @abstractmethod
    def find_duplicates(self, ast_trees: Dict[str, Any]) -> List[DuplicateReport]:
        """Detects cloned nodes across parsed AST trees mapping."""
        pass


class DeadCodeAnalyzer(ABC):
    """Abstract interface for identifying unused imports, constants, methods, and variables."""

    @abstractmethod
    def find_dead_code(
        self,
        files: List[str],
        symbols: Dict[str, Symbol],
        imports: Dict[str, List[Any]],
        call_graph: CallGraph,
    ) -> DeadCodeReport:
        """Analyzes active usage references to locate unused or unreachable code definitions."""
        pass


class SemanticSearcher(ABC):
    """Abstract interface for searching code symbols semantically."""

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[SemanticSearchResult]:
        """Queries local symbol databases for semantic matches matching terms."""
        pass


class CacheProvider(ABC):
    """Abstract interface for saving and reloading code intelligence analysis caches."""

    @abstractmethod
    def get(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Loads cached intelligence result dictionary for path."""
        pass

    @abstractmethod
    def set(self, file_path: str, value: Dict[str, Any]) -> None:
        """Saves intelligence analysis payload for path."""
        pass

    @abstractmethod
    def save(self) -> None:
        """Persists memory state cache to disk."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Cleans and deletes the cache database."""
        pass


class IntelligenceAnalyzer(ABC):
    """Main Orchestrator API abstraction for complete Code Intelligence capabilities."""

    @abstractmethod
    def analyze_repository(self, workspace_path: str) -> IntelligenceReport:
        """Performs full workspace code scans compiling ASTs, graphs, and indexes."""
        pass
