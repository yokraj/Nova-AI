"""Abstract base interfaces and contracts for AI Software Copilot components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.copilot.models import (
    ArchitectureDesign,
    BugReport,
    CodeFile,
    CodeReviewResult,
    CopilotHealth,
    CopilotMetrics,
    DeploymentConfig,
    DocumentationSet,
    ProjectState,
    RefactorPlan,
    RequirementDocument,
    TechStack,
    TestReport,
)


class IRequirementAnalyzer(ABC):
    """Requirement Analysis Engine contract."""

    @abstractmethod
    async def analyze_requirements(self, prompt: str, project_name: str = "NovaProject") -> RequirementDocument:
        """Converts raw requirements prompt into structured RequirementDocument."""
        pass


class ISoftwareArchitectureEngine(ABC):
    """Software Architecture Engine contract."""

    @abstractmethod
    async def design_architecture(self, reqs: RequirementDocument) -> ArchitectureDesign:
        """Generates system architecture, folder structure, service boundaries, database schemas."""
        pass


class ITechnologySelector(ABC):
    """Technology Selection Engine contract."""

    @abstractmethod
    async def select_technologies(self, reqs: RequirementDocument, arch: ArchitectureDesign) -> TechStack:
        """Selects technologies, frameworks, databases, and tooling."""
        pass


class ICodeGenerator(ABC):
    """Code Generation Engine contract."""

    @abstractmethod
    async def generate_code(self, reqs: RequirementDocument, arch: ArchitectureDesign, stack: TechStack) -> List[CodeFile]:
        """Generates source code files across backend, frontend, database, and infrastructure."""
        pass


class ICodeUnderstandingEngine(ABC):
    """Code Understanding Engine contract."""

    @abstractmethod
    async def analyze_repository(self, project_path: str) -> Dict[str, Any]:
        """Reads repositories, traces execution, detects patterns, and explains architecture."""
        pass


class IDebugEngine(ABC):
    """Debugging Engine contract."""

    @abstractmethod
    async def debug_code(self, file_path: str, stack_trace: str) -> BugReport:
        """Locates root causes, suggests fixes, applies patches, and verifies fixes."""
        pass


class IRefactorEngine(ABC):
    """Refactoring Engine contract."""

    @abstractmethod
    async def refactor_code(self, file_path: str, source_code: str, goal: str) -> RefactorPlan:
        """Improves architecture, reduces duplication, and optimizes performance."""
        pass


class ITestEngine(ABC):
    """Test Engineering contract."""

    @abstractmethod
    async def run_tests(self, project_path: str) -> TestReport:
        """Generates and executes unit, integration, API, UI, and security tests."""
        pass


class IDevOpsEngine(ABC):
    """DevOps Engine contract."""

    @abstractmethod
    async def configure_deployment(self, project_path: str, stack: TechStack) -> DeploymentConfig:
        """Generates Docker, CI/CD pipelines, cloud deployment, and monitoring setups."""
        pass


class IDocumentationEngine(ABC):
    """Documentation Engine contract."""

    @abstractmethod
    async def generate_documentation(self, project_state: ProjectState) -> DocumentationSet:
        """Generates README, API docs, architecture guides, and user manuals."""
        pass


class ICodeReviewEngine(ABC):
    """Code Review Engine contract."""

    @abstractmethod
    async def review_project(self, files: List[CodeFile]) -> CodeReviewResult:
        """Evaluates code quality, security, performance, naming, and maintainability."""
        pass


class IProjectManager(ABC):
    """Project Memory Store contract."""

    @abstractmethod
    async def get_project(self, project_id: str) -> Optional[ProjectState]:
        """Retrieves project tracking memory state."""
        pass

    @abstractmethod
    async def save_project(self, project: ProjectState) -> None:
        """Saves project tracking memory state."""
        pass


class ICopilotManager(ABC):
    """Copilot Manager administrative contract."""

    @abstractmethod
    async def start(self) -> None:
        """Starts copilot runtime."""
        pass

    @abstractmethod
    async def pause(self) -> None:
        """Pauses copilot processing."""
        pass

    @abstractmethod
    async def resume(self) -> None:
        """Resumes copilot processing."""
        pass


class ICopilotEngine(ABC):
    """Central AI Software Copilot Engine facade contract."""

    @abstractmethod
    async def create_project(self, prompt: str, name: str = "NovaProject", **kwargs: Any) -> ProjectState:
        """Full SDLC: requirement analysis, architecture, tech stack, code gen, tests, docs, deploy."""
        pass

    @abstractmethod
    async def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Understands existing codebase and dependency structure."""
        pass

    @abstractmethod
    async def generate_architecture(self, prompt: str) -> ArchitectureDesign:
        """Generates system architecture from requirements."""
        pass

    @abstractmethod
    async def generate_code(self, prompt: str, project_id: Optional[str] = None) -> List[CodeFile]:
        """Generates multi-file source code implementation."""
        pass

    @abstractmethod
    async def debug_project(self, project_path: str, stack_trace: str) -> BugReport:
        """Finds bugs, applies fixes, and verifies patches."""
        pass

    @abstractmethod
    async def refactor_project(self, project_path: str, goal: str) -> RefactorPlan:
        """Refactors codebase for performance and readability."""
        pass

    @abstractmethod
    async def test_project(self, project_path: str) -> TestReport:
        """Generates and executes automated test suites."""
        pass

    @abstractmethod
    async def deploy_project(self, project_path: str) -> DeploymentConfig:
        """Generates Docker and CI/CD deployment configurations."""
        pass

    @abstractmethod
    async def review_project(self, project_path: str) -> CodeReviewResult:
        """Performs security, performance, and architecture review."""
        pass

    @abstractmethod
    async def document_project(self, project_id: str) -> DocumentationSet:
        """Generates full documentation suite."""
        pass
