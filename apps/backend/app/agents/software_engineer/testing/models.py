"""Pydantic schemas representing testing plans, coverages, benchmarks and security results.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TestTask(BaseModel):
    """Refers to a single test generation task."""

    __test__ = False

    id: str
    target_module: str
    test_type: str = Field("unit", description="Category: unit, integration, api, ui")
    instructions: str
    dependencies: List[str] = Field(default_factory=list)
    status: str = Field("pending")


class TestPlan(BaseModel):
    """Decomposition of testing request into dependency-mapped steps."""

    __test__ = False

    plan_id: str
    request_summary: str
    tasks: List[TestTask] = Field(default_factory=list)
    risk_profile: str = Field("low")


class TestRequest(BaseModel):
    """Parameters to request test suite generations and executions."""

    __test__ = False

    prompt: str = Field(..., description="Target module testing instructions.")
    file_path: Optional[str] = Field(None, description="Optional target file path to generate tests for.")
    model_override: Optional[str] = Field(None)
    temperature: float = Field(0.2)
    max_tokens: int = Field(4096)


class TestResult(BaseModel):
    """Outcome of a single test case execution."""

    __test__ = False

    name: str
    status: str = Field(..., description="passed, failed, skipped, error")
    duration: float = Field(0.0)
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None


class TestSuite(BaseModel):
    """Outcome collection of a complete test file run."""

    __test__ = False

    suite_name: str
    results: List[TestResult] = Field(default_factory=list)
    passed_count: int = Field(0)
    failed_count: int = Field(0)
    duration: float = Field(0.0)


class CoverageReport(BaseModel):
    """Workspace files coverage details."""

    overall_percentage: float = Field(0.0)
    file_coverages: Dict[str, float] = Field(default_factory=dict, description="Map of relative file paths to coverage ratios.")
    untested_symbols: List[str] = Field(default_factory=list)


class BenchmarkReport(BaseModel):
    """Latency and resource benchmarks report."""

    execution_time: float = Field(0.0)
    memory_usage_bytes: int = Field(0)
    cpu_usage_percentage: float = Field(0.0)
    startup_latency: float = Field(0.0)


class FailureReport(BaseModel):
    """Analysis of failed assertions and exception tracebacks."""

    failure_type: str = Field(..., description="assertion, runtime_exception, timeout, import_error")
    message: str
    traceback: Optional[str] = None
    failing_line_number: Optional[int] = None


class RepairSuggestion(BaseModel):
    """Refactoring suggestions proposed by local AI model for failing tests."""

    target_test_file: str
    failing_test_name: str
    recommended_patch: str = Field(..., description="Suggested code diff or replacements block.")
    explanation: str


class QualityMetrics(BaseModel):
    """Quality and maintainability indices."""

    maintainability_index: float = Field(100.0)
    test_coverage: float = Field(0.0)
    complexity_score: int = Field(0)
    duplication_percentage: float = Field(0.0)
    technical_debt_ratio: float = Field(0.0)
    code_smells_count: int = Field(0)
    documentation_quality: float = Field(100.0)


class SecurityFinding(BaseModel):
    """Vulnerabilities detected by security scanner."""

    file_path: str
    rule_id: str
    severity: str = Field("medium", description="info, low, medium, high")
    message: str
    line_number: int


class StaticAnalysisReport(BaseModel):
    """Static checks reports."""

    is_compliant: bool
    style_violations: List[str] = Field(default_factory=list)
    architecture_violations: List[str] = Field(default_factory=list)


class TestStatistics(BaseModel):
    """Aggregated stats representing test suite execution run."""

    __test__ = False

    total_tests: int = Field(0)
    passed: int = Field(0)
    failed: int = Field(0)
    duration: float = Field(0.0)


class ExecutionMetrics(BaseModel):
    """Resource consumption ratios."""

    cpu_usage: float = Field(0.0)
    memory_usage_mb: float = Field(0.0)


class ValidationReport(BaseModel):
    """Syntax correctness checks report."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)


class TestHistory(BaseModel):
    """Historical records of test runs."""

    __test__ = False

    history_entries: List[Dict[str, Any]] = Field(default_factory=list)


class TestingContext(BaseModel):
    """Context gathered before calling AI models to write tests."""

    __test__ = False

    workspace_root: str
    target_module: Optional[str] = None
    existing_tests_count: int = Field(0)
    related_symbols: List[str] = Field(default_factory=list)
    style_guidelines: Optional[Dict[str, Any]] = None
