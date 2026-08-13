"""Pydantic v2 models representing debugging sessions, tracebacks frames, and reports schemas.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DebugRequest(BaseModel):
    """Parameters representing a debugging session request."""

    traceback_str: str = Field(..., description="Stack trace or logs to diagnose.")
    prompt: Optional[str] = Field(None, description="Optional description of context.")
    model_override: Optional[str] = Field(None)
    temperature: float = Field(0.2)
    max_tokens: int = Field(4096)


class StackFrame(BaseModel):
    """A single frame in a parsed traceback call stack."""

    file_path: str
    line_number: int
    function_name: str
    code_line: Optional[str] = None


class StackTrace(BaseModel):
    """Collection representing a complete stack trace call stack."""

    raw_text: str
    frames: List[StackFrame] = Field(default_factory=list)
    exception_type: str
    exception_message: str


class FailureClassification(BaseModel):
    """Classification details identifying categories of failure."""

    category: str = Field(..., description="logic, runtime, api, db, security, syntax, config, etc.")
    explanation: str


class RootCause(BaseModel):
    """Detailed findings pinpointing the origin of code failure."""

    origin_file: str
    origin_function: str
    origin_class: Optional[str] = None
    failure_chain: List[str] = Field(default_factory=list)
    affected_modules: List[str] = Field(default_factory=list)
    potential_causes: List[str] = Field(default_factory=list)
    confidence_score: float = Field(0.0)


class RepairSuggestion(BaseModel):
    """A single code fix suggestion proposed by LLM."""

    file_path: str
    original_code: str
    replacement_code: str
    explanation: str


class RepairPlan(BaseModel):
    """Decomposition of code modifications required to resolve failures."""

    plan_id: str
    summary: str
    suggestions: List[RepairSuggestion] = Field(default_factory=list)
    estimated_risk: str = Field("low", description="low, medium, high")
    confidence_score: float = Field(0.0)


class RepairValidation(BaseModel):
    """Outcomes of compiling and checking proposed fixes syntax checks."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)


class ConfidenceReport(BaseModel):
    """Quality estimates representing debugging success probabilities."""

    root_cause_confidence: float = Field(0.0)
    repair_confidence: float = Field(0.0)
    overall_success_probability: float = Field(0.0)


class DependencyIssue(BaseModel):
    """Identified dependency graph conflict or import warning."""

    package_name: str
    issue_type: str = Field(..., description="missing_package, version_conflict, circular_import")
    message: str


class ImportIssue(BaseModel):
    """Import validation issues."""

    file_path: str
    issue_type: str = Field(..., description="unused_import, cyclic_import, missing_import")
    message: str
    line_number: int


class RuntimeIssue(BaseModel):
    """Identified async execution or task cancellation issue."""

    issue_type: str = Field(..., description="async_timeout, task_cancellation, middleware_failure")
    message: str


class MemoryIssue(BaseModel):
    """Memory consumption concerns or large allocations trends."""

    issue_type: str = Field(..., description="leak_alert, large_allocation, cache_misuse")
    message: str
    estimated_leak_size_bytes: Optional[int] = None


class PerformanceIssue(BaseModel):
    """Performance hotspots identified by static or dynamic profiling."""

    issue_type: str = Field(..., description="slow_loop, recursion_bottleneck, blocking_call")
    message: str
    estimated_latency_ms: Optional[float] = None


class Failure(BaseModel):
    """Details representing a single diagnosed codebase failure."""

    traceback: StackTrace
    classification: FailureClassification
    root_cause: RootCause


class DebugStatistics(BaseModel):
    """Accumulated stats representing debugging sessions."""

    total_sessions: int = Field(0)
    resolved_count: int = Field(0)
    average_confidence: float = Field(0.0)


class DebugReport(BaseModel):
    """Consolidated final debugging report containing logs summaries and fixes."""

    session_id: str
    failure: Failure
    repair_plan: Optional[RepairPlan] = None
    validation: Optional[RepairValidation] = None
    confidence: ConfidenceReport
    statistics: Optional[DebugStatistics] = None
    markdown_report: str


class DebugContext(BaseModel):
    """System context compiled before calling local AI models."""

    workspace_root: str
    scanned_files_count: int
    related_symbols: List[str] = Field(default_factory=list)
    environment_variables: Dict[str, str] = Field(default_factory=dict)


class DebugSession(BaseModel):
    """An active tracking state session for debugging workflows."""

    session_id: str
    request: DebugRequest
    context: DebugContext
    report: Optional[DebugReport] = None
    start_time: float
