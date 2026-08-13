"""Abstract base interfaces and contracts for Autonomous AI Software Engineering Company.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional
from app.ai.software_company.models import (
    CompanyHealth,
    ProjectBuildResult,
    ProjectDashboardStatus,
    ProjectMemoryItem,
    SoftwareArchitectureBlueprint,
    SoftwareProjectSpec,
)


class IProjectRequirementsDivision(ABC):
    """Contract for Project Requirements Division."""

    @abstractmethod
    async def extract_requirements(self, user_prompt: str) -> SoftwareProjectSpec:
        """Translates user prompt into full Software Requirements Specification (SRS)."""
        pass


class ISystemArchitectureDivision(ABC):
    """Contract for System Architecture Division."""

    @abstractmethod
    async def design_architecture(self, spec: SoftwareProjectSpec) -> SoftwareArchitectureBlueprint:
        """Designs system architecture blueprint and component hierarchy."""
        pass


class IProjectFactoryEngine(ABC):
    """Contract for Autonomous Project Factory pipeline."""

    @abstractmethod
    async def build_project(self, prompt: str) -> ProjectBuildResult:
        """Executes full automated software lifecycle factory pipeline."""
        pass


class IContinuousProjectMemory(ABC):
    """Contract for Continuous Project Memory."""

    @abstractmethod
    def store_memory(self, project_id: str, category: str, content: Any) -> ProjectMemoryItem:
        """Stores project memory item."""
        pass

    @abstractmethod
    def get_project_history(self, project_id: str) -> List[ProjectMemoryItem]:
        """Retrieves project history and architectural memory."""
        pass


class IVoiceSoftwareCompany(ABC):
    """Contract for Voice-Driven Software Company."""

    @abstractmethod
    async def process_voice_project_request(self, voice_prompt: str) -> Dict[str, Any]:
        """Maps natural voice request to end-to-end software factory execution."""
        pass


class IAutonomousSoftwareCompanyEngine(ABC):
    """Central facade contract for Autonomous AI Software Engineering Company."""

    @abstractmethod
    async def build_software(self, prompt: str) -> ProjectBuildResult:
        """Builds complete production-grade software project from prompt."""
        pass

    @abstractmethod
    def get_company_health(self) -> CompanyHealth:
        """Snapshot company health metrics."""
        pass
