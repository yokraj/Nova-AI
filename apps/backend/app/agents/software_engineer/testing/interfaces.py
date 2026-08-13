"""Abstract interfaces outlining testing and QA component boundaries.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.agents.software_engineer.testing.models import (
    BenchmarkReport,
    CoverageReport,
    FailureReport,
    QualityMetrics,
    RepairSuggestion,
    SecurityFinding,
    StaticAnalysisReport,
    TestSuite,
    TestPlan,
    TestRequest,
    TestingContext,
    ValidationReport,
)
from app.agents.software_engineer.generator.models import PromptPackage


class TestPlanner(ABC):
    """Decomposes test request goals prioritizing coverage weaknesses."""

    @abstractmethod
    def plan_testing(
        self, request: TestRequest, context: TestingContext
    ) -> TestPlan:
        """Formulates testing task execution steps."""
        pass


class ContextBuilder(ABC):
    """Gathers repository file logs and mock context."""

    @abstractmethod
    def build_context(
        self, request: TestRequest, workspace_path: str
    ) -> TestingContext:
        """Assembles module parameters and styles guidelines into testing contexts."""
        pass


class PromptBuilder(ABC):
    """Constructs prompt message package instructing active local coding models."""

    @abstractmethod
    def build_prompt(
        self, request: TestRequest, context: TestingContext, task_instructions: str
    ) -> PromptPackage:
        """Packages instructions for generating test suites."""
        pass


class TestGenerator(ABC):
    """Base interface generating test suites."""

    @abstractmethod
    def generate_tests(
        self, request: TestRequest, context: TestingContext, instructions: str
    ) -> str:
        """Generates source code string representing pytest suites."""
        pass


class CoverageAnalyzer(ABC):
    """Computes branch and symbol coverages across files."""

    @abstractmethod
    def analyze_coverage(self, workspace_path: str) -> CoverageReport:
        """Analyzes missing tests and reports coverage statistics."""
        pass


class TestRunner(ABC):
    """Main interface coordinating executing test run triggers."""

    @abstractmethod
    def run_tests(
        self, workspace_path: str, test_file_path: str
    ) -> TestSuite:
        """Runs the pytest suite returning test results collection."""
        pass


class TestExecutor(ABC):
    """Manages queue execution and threads/processes policies."""

    @abstractmethod
    def execute_queue(
        self, workspace_path: str, tests_to_run: List[str]
    ) -> List[TestSuite]:
        """Manages queue worker runs including timeout limits."""
        pass


class FailureAnalyzer(ABC):
    """Identifies failure types and lines parsing stack traces."""

    @abstractmethod
    def analyze_failure(self, traceback_str: str) -> FailureReport:
        """Maps traceback string to diagnostic reports."""
        pass


class RepairEngine(ABC):
    """Suggests fixes for failed assertions."""

    @abstractmethod
    def suggest_repairs(
        self, failure: FailureReport, context: TestingContext
    ) -> RepairSuggestion:
        """Formulates code fix recommendations."""
        pass


class BenchmarkEngine(ABC):
    """Gathers metrics representing execution latency and resource footprints."""

    @abstractmethod
    def measure_performance(self, execution_callback: Any, *args: Any, **kwargs: Any) -> BenchmarkReport:
        """Gathers system latency, CPU usage and memory parameters."""
        pass


class StaticAnalyzer(ABC):
    """Inspects imports validation and stylistic alignments."""

    @abstractmethod
    def analyze_static(self, workspace_path: str, file_path: str) -> StaticAnalysisReport:
        """Runs static AST validation checks on the target file path."""
        pass


class SecurityScanner(ABC):
    """Identifies hardcoded secrets or sql injection risks."""

    @abstractmethod
    def scan_security(self, workspace_path: str, file_path: str) -> List[SecurityFinding]:
        """Performs static regex rules match scanner checks."""
        pass


class ReportGenerator(ABC):
    """Produces quality and verification reports logs."""

    @abstractmethod
    def generate_html_report(
        self, suite: TestSuite, coverage: CoverageReport, metrics: QualityMetrics
    ) -> str:
        """Formats quality and benchmarks details as HTML content."""
        pass


class TestingEngine(ABC):
    """Central orchestrator managing test generation, scans, benchmarks and quality reports."""

    @abstractmethod
    async def execute_testing_pipeline(self, request: TestRequest) -> Dict[str, Any]:
        """Runs complete verification quality suite pipeline."""
        pass
