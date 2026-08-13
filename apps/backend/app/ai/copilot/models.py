"""Pydantic data models, enums, and structures for AI Software Copilot.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class ProjectLanguage(str, Enum):
    """Enumerate supported programming languages."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    FLUTTER = "flutter"
    HTML_CSS = "html_css"


class ArchitectureStyle(str, Enum):
    """Enumerate architectural styles."""

    MONOLITH = "monolith"
    MODULAR_MONOLITH = "modular_monolith"
    MICROSERVICES = "microservices"
    EVENT_DRIVEN = "event_driven"
    SERVERLESS = "serverless"


class SDLCStage(str, Enum):
    """Enumerate Software Development Life Cycle stages."""

    REQUIREMENTS = "requirements"
    ARCHITECTURE = "architecture"
    TECH_SELECTION = "tech_selection"
    CODE_GENERATION = "code_generation"
    UNDERSTANDING = "understanding"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    CODE_REVIEW = "code_review"
    COMPLETED = "completed"


class CopilotState(str, Enum):
    """Enumerate state of AI Software Copilot."""

    IDLE = "IDLE"
    ANALYZING = "ANALYZING"
    DESIGNING = "DESIGNING"
    GENERATING = "GENERATING"
    DEBUGGING = "DEBUGGING"
    REFACTORING = "REFACTORING"
    TESTING = "TESTING"
    DEPLOYING = "DEPLOYING"
    ERROR = "ERROR"
    PAUSED = "PAUSED"


class RequirementDocument(BaseModel):
    """Structured requirements document extracted from natural language prompt."""

    doc_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    project_name: str = Field(..., description="Project name")
    business_goals: List[str] = Field(default_factory=list)
    functional_requirements: List[str] = Field(default_factory=list)
    non_functional_requirements: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    technology_preferences: List[str] = Field(default_factory=list)
    security_requirements: List[str] = Field(default_factory=list)
    performance_targets: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)


class TechStack(BaseModel):
    """Technology choices for the project."""

    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    messaging: List[str] = Field(default_factory=list)
    containerization: List[str] = Field(default_factory=list)
    cloud_providers: List[str] = Field(default_factory=list)
    testing_frameworks: List[str] = Field(default_factory=list)
    dev_tools: List[str] = Field(default_factory=list)


class ArchitectureDesign(BaseModel):
    """Structured system architecture specification."""

    design_id: str = Field(default_factory=lambda: f"arch_{uuid.uuid4().hex[:8]}")
    style: ArchitectureStyle = Field(ArchitectureStyle.MODULAR_MONOLITH)
    folder_structure: Dict[str, Any] = Field(default_factory=dict)
    service_boundaries: List[str] = Field(default_factory=list)
    database_architecture: Dict[str, Any] = Field(default_factory=dict)
    api_architecture: Dict[str, Any] = Field(default_factory=dict)
    frontend_architecture: Dict[str, Any] = Field(default_factory=dict)
    backend_architecture: Dict[str, Any] = Field(default_factory=dict)
    caching_strategy: str = Field("redis_in_memory")
    auth_strategy: str = Field("jwt_bearer_oauth2")
    logging_monitoring: str = Field("structured_json_telemetry")
    deployment_architecture: str = Field("docker_compose_containerized")


class CodeFile(BaseModel):
    """Represents a single generated or edited code file."""

    path: str = Field(..., description="Relative file path")
    content: str = Field(..., description="File source code content")
    language: str = Field("python")
    file_type: str = Field("source", description="Type (source, test, config, doc, build)")
    exports: List[str] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class BugReport(BaseModel):
    """Automated bug detection and repair report."""

    bug_id: str = Field(default_factory=lambda: f"bug_{uuid.uuid4().hex[:8]}")
    title: str = Field(...)
    stack_trace: Optional[str] = Field(None)
    file_path: str = Field(...)
    line_number: Optional[int] = Field(None)
    root_cause: str = Field(...)
    suggested_fix: str = Field(...)
    fix_code: Optional[str] = Field(None)
    verified: bool = Field(False)


class RefactorPlan(BaseModel):
    """Code refactoring plan and transformation proposal."""

    plan_id: str = Field(default_factory=lambda: f"ref_{uuid.uuid4().hex[:8]}")
    target_file: str = Field(...)
    refactor_goal: str = Field(...)
    architectural_improvements: List[str] = Field(default_factory=list)
    simplified_code: str = Field(...)
    performance_impact: str = Field("improved")


class TestReport(BaseModel):
    """Test execution suite report."""

    report_id: str = Field(default_factory=lambda: f"tst_{uuid.uuid4().hex[:8]}")
    test_types: List[str] = Field(default_factory=list)
    total_tests: int = Field(0)
    passed_tests: int = Field(0)
    failed_tests: int = Field(0)
    coverage_percent: float = Field(0.0)
    failure_details: List[Dict[str, Any]] = Field(default_factory=list)


class DeploymentConfig(BaseModel):
    """DevOps deployment setup specification."""

    target: str = Field("local_docker")
    container_spec: Dict[str, Any] = Field(default_factory=dict)
    ci_cd_pipeline: Dict[str, Any] = Field(default_factory=dict)
    rollback_plan: str = Field("automatic_previous_image_rollback")
    monitoring_setup: str = Field("prometheus_grafana_telemetry")
    environment_vars: Dict[str, str] = Field(default_factory=dict)


class CodeReviewResult(BaseModel):
    """Code review findings and evaluation report."""

    review_id: str = Field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:8]}")
    score: float = Field(100.0, description="Overall score out of 100")
    performance_issues: List[str] = Field(default_factory=list)
    security_vulnerabilities: List[str] = Field(default_factory=list)
    style_violations: List[str] = Field(default_factory=list)
    maintainability_score: float = Field(90.0)
    suggestions: List[str] = Field(default_factory=list)


class DocumentationSet(BaseModel):
    """Complete software project documentation set."""

    doc_id: str = Field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:8]}")
    readme_md: str = Field("")
    api_docs: str = Field("")
    architecture_md: str = Field("")
    developer_guide: str = Field("")
    user_guide: str = Field("")
    deployment_guide: str = Field("")
    changelog: str = Field("")


class ProjectState(BaseModel):
    """Complete project tracking memory state."""

    project_id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:8]}")
    name: str = Field(...)
    path: str = Field(...)
    language: ProjectLanguage = Field(ProjectLanguage.PYTHON)
    stage: SDLCStage = Field(SDLCStage.REQUIREMENTS)
    files: List[CodeFile] = Field(default_factory=list)
    requirements: Optional[RequirementDocument] = Field(None)
    architecture: Optional[ArchitectureDesign] = Field(None)
    tech_stack: Optional[TechStack] = Field(None)
    active_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    open_bugs: List[BugReport] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    updated_at: float = Field(default_factory=time.time)


class CopilotMetrics(BaseModel):
    """Telemetry collector metrics model."""

    projects_created: int = Field(0)
    lines_generated: int = Field(0)
    bugs_fixed: int = Field(0)
    tests_passed: int = Field(0)
    deployments_completed: int = Field(0)
    average_latency_ms: float = Field(0.0)
    timestamp: float = Field(default_factory=time.time)


class CopilotHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    copilot_state: CopilotState = Field(CopilotState.IDLE)
    active_projects_count: int = Field(0)
    loaded_engines: List[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)
