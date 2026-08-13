"""Interfaces for the Enterprise Software Deployment Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.agents.software_engineer.deployment.models import (
    DeploymentRequest,
    DeploymentPlan,
    EnvironmentInfo,
    BuildResult,
    DockerConfiguration,
    PipelineConfiguration,
    DeploymentArtifact,
    ReleaseVersion,
    RollbackPlan,
    HealthCheck,
    DeploymentReport,
)

class IEnvironmentAnalyzer(ABC):
    """Abstract interface for detecting environment information."""

    @abstractmethod
    def analyze(self, project_path: str) -> EnvironmentInfo:
        """Analyzes a project directory and returns detected language/framework info."""
        pass

class IBuildManager(ABC):
    """Abstract interface for build planning and validation."""

    @abstractmethod
    def validate_build_readiness(self, project_path: str, env_info: EnvironmentInfo) -> BuildResult:
        """Validates compilation, dependencies, and test execution."""
        pass

class IContainerGenerator(ABC):
    """Abstract interface for Docker configuration generation."""

    @abstractmethod
    def generate(self, project_path: str, env_info: EnvironmentInfo) -> DockerConfiguration:
        """Generates Dockerfile and Docker Compose configurations."""
        pass

class IPipelineGenerator(ABC):
    """Abstract interface for pipeline generation (GitHub, GitLab, Jenkins)."""

    @abstractmethod
    def generate(self, project_path: str, env_info: EnvironmentInfo) -> PipelineConfiguration:
        """Generates CI/CD configuration files."""
        pass

class IValidator(ABC):
    """Abstract interface for post-generation/pre-deployment validation."""

    @abstractmethod
    def validate(
        self,
        project_path: str,
        docker_config: Optional[DockerConfiguration] = None,
        pipeline_config: Optional[PipelineConfiguration] = None,
    ) -> List[str]:
        """Validates generated configs and returns a list of validation errors."""
        pass

class IReleaseManager(ABC):
    """Abstract interface for release tracking and preparation."""

    @abstractmethod
    def prepare_release(self, project_path: str, current_version: str) -> ReleaseVersion:
        """Prepares a new release version, tagging, and changelogs."""
        pass

class IRollbackManager(ABC):
    """Abstract interface for version rollback plans."""

    @abstractmethod
    def generate_rollback_plan(self, current_version: str, target_version: str) -> RollbackPlan:
        """Generates rollback instructions."""
        pass

class IArtifactManager(ABC):
    """Abstract interface for artifact management."""

    @abstractmethod
    def track_artifact(self, artifact: DeploymentArtifact) -> None:
        """Tracks deployment artifacts."""
        pass

    @abstractmethod
    def list_artifacts(self) -> List[DeploymentArtifact]:
        """Lists tracked deployment artifacts."""
        pass

class IMonitoringConfigurator(ABC):
    """Abstract interface for configuring logging, monitoring, and observability templates."""

    @abstractmethod
    def configure(self, project_path: str, env_info: EnvironmentInfo) -> Dict[str, Any]:
        """Generates Prometheus rules, Grafana charts, and logging configurations."""
        pass

class IDeploymentEngine(ABC):
    """Abstract interface for the orchestrating Deployment Engine."""

    @abstractmethod
    async def prepare_deployment(self, request: DeploymentRequest) -> DeploymentReport:
        """Executes the full 11-stage autonomous deployment preparation pipeline."""
        pass
