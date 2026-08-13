"""Pydantic V2 data models and schemas for Autonomous AI Software Engineering Company.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class ProjectStage(str, Enum):
    """Enumerate stages of the Autonomous Project Factory software development lifecycle."""

    REQUIREMENTS = "REQUIREMENTS"
    ARCHITECTURE = "ARCHITECTURE"
    UI_UX_DESIGN = "UI_UX_DESIGN"
    DATABASE_DESIGN = "DATABASE_DESIGN"
    BACKEND_DEVELOPMENT = "BACKEND_DEVELOPMENT"
    FRONTEND_DEVELOPMENT = "FRONTEND_DEVELOPMENT"
    MOBILE_DEVELOPMENT = "MOBILE_DEVELOPMENT"
    TESTING_QA = "TESTING_QA"
    CODE_REVIEW = "CODE_REVIEW"
    DEBUGGING_AUTOFIX = "DEBUGGING_AUTOFIX"
    DEVOPS_DEPLOYMENT = "DEVOPS_DEPLOYMENT"
    DOCUMENTATION = "DOCUMENTATION"
    PROJECT_MANAGEMENT = "PROJECT_MANAGEMENT"
    DELIVERED = "DELIVERED"
    MAINTENANCE = "MAINTENANCE"


class BuildStatus(str, Enum):
    """Build status of a software factory project."""

    INITIALIZING = "INITIALIZING"
    IN_PROGRESS = "IN_PROGRESS"
    TESTING = "TESTING"
    AUTO_FIXING = "AUTO_FIXING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class SoftwareProjectSpec(BaseModel):
    """Project requirements specification produced by Requirements Division."""

    project_id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:8]}")
    title: str = Field(...)
    user_prompt: str = Field(...)
    srs_document: str = Field(...)
    user_stories: List[str] = Field(default_factory=list)
    functional_requirements: List[str] = Field(default_factory=list)
    tech_stack: Dict[str, str] = Field(default_factory=lambda: {"backend": "FastAPI", "frontend": "React", "database": "PostgreSQL"})
    created_at: float = Field(default_factory=time.time)


class SoftwareArchitectureBlueprint(BaseModel):
    """System architecture blueprint produced by Architecture Division."""

    blueprint_id: str = Field(default_factory=lambda: f"arch_{uuid.uuid4().hex[:8]}")
    project_id: str = Field(...)
    components: List[str] = Field(default_factory=list)
    folder_structure: List[str] = Field(default_factory=list)
    caching_strategy: str = Field("Redis In-Memory Cache")
    deployment_topology: str = Field("Docker Containerized Microservices")


class DBSchemaSpec(BaseModel):
    """Database schema specification produced by Database Division."""

    schema_id: str = Field(default_factory=lambda: f"db_{uuid.uuid4().hex[:8]}")
    tables: List[str] = Field(default_factory=list)
    migration_scripts: List[str] = Field(default_factory=list)
    indexes: List[str] = Field(default_factory=list)


class APIEndpointSpec(BaseModel):
    """API endpoint specification produced by Backend Division."""

    endpoint_id: str = Field(default_factory=lambda: f"api_{uuid.uuid4().hex[:8]}")
    method: str = Field("GET")
    path: str = Field(...)
    handler_name: str = Field(...)
    auth_required: bool = Field(True)


class ProjectBuildResult(BaseModel):
    """Final output artifact of the Autonomous Project Factory."""

    project_id: str = Field(...)
    title: str = Field(...)
    status: BuildStatus = Field(BuildStatus.SUCCESS)
    stage: ProjectStage = Field(ProjectStage.DELIVERED)
    generated_files_count: int = Field(15)
    test_coverage_percent: float = Field(92.5)
    security_audited: bool = Field(True)
    deployment_url: str = Field("http://localhost:8000")
    documentation_path: str = Field("docs/README.md")
    timestamp: float = Field(default_factory=time.time)


class ProjectMemoryItem(BaseModel):
    """Item stored in Continuous Project Memory."""

    memory_id: str = Field(default_factory=lambda: f"pmem_{uuid.uuid4().hex[:8]}")
    project_id: str = Field(...)
    category: str = Field(...)
    content: Any = Field(...)
    timestamp: float = Field(default_factory=time.time)


class ProjectDashboardStatus(BaseModel):
    """Live status snapshot for Project Dashboard."""

    company_name: str = Field("Nova Autonomous Software Engineering Co.")
    active_projects_count: int = Field(1)
    current_stage: ProjectStage = Field(ProjectStage.DELIVERED)
    build_status: BuildStatus = Field(BuildStatus.SUCCESS)
    test_coverage_percent: float = Field(92.5)
    bugs_fixed_count: int = Field(2)
    uptime_seconds: float = Field(3600.0)


class CompanyHealth(BaseModel):
    """Health diagnostic metrics for Nova Software Engineering Company."""

    is_healthy: bool = Field(True)
    status: str = Field("HEALTHY")
    engineering_divisions_count: int = Field(13)
    total_factory_agents: int = Field(73)
    project_factory_active: bool = Field(True)
    timestamp: float = Field(default_factory=time.time)
