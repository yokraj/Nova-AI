"""Abstract interfaces outlining boundaries for all debugging components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.agents.software_engineer.debugging.models import (
    ConfidenceReport,
    DebugContext,
    DependencyIssue,
    FailureClassification,
    ImportIssue,
    MemoryIssue,
    PerformanceIssue,
    RepairPlan,
    RepairValidation,
    RootCause,
    RuntimeIssue,
    StackTrace,
    DebugRequest,
    DebugReport,
)


class DebugPlanner(ABC):
    """Decomposes debug goals into targeted diagnosis steps."""

    @abstractmethod
    def plan_debugging(
        self, request: DebugRequest, context: DebugContext
    ) -> List[str]:
        """Formulates diagnostic tasks list."""
        pass


class StackTraceParser(ABC):
    """Extracts filenames, lines, and method frames from raw logs."""

    @abstractmethod
    def parse_traceback(self, traceback_str: str) -> StackTrace:
        """Parses raw text trace blocks into StackTrace models."""
        pass


class RootCauseAnalyzer(ABC):
    """Traces execution layers context to locate crash locations."""

    @abstractmethod
    def detect_root_cause(
        self, traceback: StackTrace, context: DebugContext
    ) -> RootCause:
        """Traces origin file and potential causes."""
        pass


class FailureClassifier(ABC):
    """Categorizes failures types (logic, runtime, api, etc.)."""

    @abstractmethod
    def classify_failure(self, traceback: StackTrace) -> FailureClassification:
        """Maps traceback keywords to classifications categories."""
        pass


class DependencyChecker(ABC):
    """Validates packages graphs and version constraints compatibility."""

    @abstractmethod
    def check_dependencies(self, workspace_path: str) -> List[DependencyIssue]:
        """Checks package manifest configurations."""
        pass


class ImportValidator(ABC):
    """Scans syntax import structures checking cyclical/shadowed cases."""

    @abstractmethod
    def validate_imports(self, workspace_path: str, file_path: str) -> List[ImportIssue]:
        """Validates python import directives."""
        pass


class RuntimeAnalyzer(ABC):
    """Audits async loops execution trace logs."""

    @abstractmethod
    def analyze_runtime(self, log_lines: List[str]) -> List[RuntimeIssue]:
        """Analyzes event loop cancellations or scheduler pipeline failures."""
        pass


class MemoryAnalyzer(ABC):
    """Scans collections or structures for allocation leaks leaks."""

    @abstractmethod
    def analyze_memory(self, workspace_path: str, file_path: str) -> List[MemoryIssue]:
        """Runs static analysis check for leaks or memory bloats."""
        pass


class PerformanceAnalyzer(ABC):
    """Identifies recursive limits or latency hotspots."""

    @abstractmethod
    def analyze_performance(self, workspace_path: str, file_path: str) -> List[PerformanceIssue]:
        """Profiles code files looking for slow loops or blocking operations."""
        pass


class RepairGenerator(ABC):
    """Coordinates local AI model calls via AI Gateway to construct patches."""

    @abstractmethod
    async def generate_repair(
        self, request: DebugRequest, context: DebugContext, root_cause: RootCause
    ) -> RepairPlan:
        """Queries local models outputting patches and risk levels."""
        pass


class RepairValidator(ABC):
    """Statically verifies generated syntax patches prior to execution."""

    @abstractmethod
    def validate_repair(self, plan: RepairPlan) -> RepairValidation:
        """Compiles proposed patches checking compile correctness."""
        pass


class ConfidenceEstimator(ABC):
    """Estimates diagnostic accuracy and repair success likelihoods."""

    @abstractmethod
    def estimate_confidence(
        self, root_cause: RootCause, plan: Optional[RepairPlan]
    ) -> ConfidenceReport:
        """Calculates confidence scales from 0.0 to 1.0."""
        pass


class BugDatabase(ABC):
    """Local offline cache holding common resolutions matching stack fingerprints."""

    @abstractmethod
    def get_known_fix(self, exception_type: str, message: str) -> Optional[RepairPlan]:
        """Looks up cached fixes templates."""
        pass

    @abstractmethod
    def record_resolution(self, exception_type: str, message: str, plan: RepairPlan) -> None:
        """Saves resolutions mappings."""
        pass


class KnowledgeBase(ABC):
    """Searchable database of debug reports logs historical resolutions."""

    @abstractmethod
    def search_knowledge(self, query: str) -> List[DebugReport]:
        """Queries historical summaries."""
        pass

    @abstractmethod
    def index_report(self, report: DebugReport) -> None:
        """Indexes debug outcomes summaries."""
        pass


class ReportGenerator(ABC):
    """Compiles markdown/HTML summaries reports layout."""

    @abstractmethod
    def generate_markdown(self, report: DebugReport) -> str:
        """Formats debug details as Markdown text."""
        pass


class DebugEngine(ABC):
    """Main entry coordinates analyzer, repair generation and report compilation."""

    @abstractmethod
    async def run_diagnose(self, request: DebugRequest) -> DebugReport:
        """Runs entire diagnosis pipeline."""
        pass
