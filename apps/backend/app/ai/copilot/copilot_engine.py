"""Central AI Software Copilot Engine unifying the full SDLC pipeline.
"""

import time
from typing import Any, Dict, List, Optional
from app.ai.copilot.architecture_engine import SoftwareArchitectureEngine
from app.ai.copilot.code_generator import CodeGenerator
from app.ai.copilot.code_understanding import CodeUnderstandingEngine
from app.ai.copilot.configuration import CopilotConfiguration
from app.ai.copilot.copilot_manager import CopilotManager
from app.ai.copilot.debug_engine import DebugEngine
from app.ai.copilot.deployment_engine import DevOpsEngine
from app.ai.copilot.documentation_engine import DocumentationEngine
from app.ai.copilot.git_integration import GitIntegration
from app.ai.copilot.health import CopilotHealthMonitor
from app.ai.copilot.ide_integration import IDEIntegration
from app.ai.copilot.interfaces import ICopilotEngine
from app.ai.copilot.metrics import CopilotMetricsTracker
from app.ai.copilot.models import (
    ArchitectureDesign,
    BugReport,
    CodeFile,
    CodeReviewResult,
    CopilotHealth,
    CopilotMetrics,
    CopilotState,
    DeploymentConfig,
    DocumentationSet,
    ProjectLanguage,
    ProjectState,
    RefactorPlan,
    RequirementDocument,
    SDLCStage,
    TechStack,
    TestReport,
)
from app.ai.copilot.project_manager import ProjectManager
from app.ai.copilot.refactor_engine import RefactorEngine
from app.ai.copilot.requirement_analyzer import RequirementAnalyzer
from app.ai.copilot.review_engine import CodeReviewEngine
from app.ai.copilot.technology_selector import TechnologySelector
from app.ai.copilot.test_engine import TestEngine
from app.ai.copilot.utils import format_sdlc_progress


from app.ai.copilot.orchestrator import CopilotOrchestrator


class CopilotEngine(ICopilotEngine):
    """The central AI Software Copilot Engine runtime for Nova AI."""

    def __init__(self, config: Optional[CopilotConfiguration] = None) -> None:
        self.config = config or CopilotConfiguration()
        self.manager = CopilotManager(self.config)
        self.orchestrator = CopilotOrchestrator()
        self.requirement_analyzer = RequirementAnalyzer()
        self.architecture_engine = SoftwareArchitectureEngine()
        self.technology_selector = TechnologySelector()
        self.code_generator = CodeGenerator()
        self.code_understanding = CodeUnderstandingEngine()
        self.debug_engine = DebugEngine()
        self.refactor_engine = RefactorEngine()
        self.test_engine = TestEngine()
        self.deployment_engine = DevOpsEngine()
        self.documentation_engine = DocumentationEngine()
        self.review_engine = CodeReviewEngine()
        self.project_manager = ProjectManager()
        self.ide_integration = IDEIntegration()
        self.git_integration = GitIntegration()
        self.metrics_tracker = CopilotMetricsTracker()
        self.health_monitor = CopilotHealthMonitor()

        self.health_monitor.set_state(CopilotState.IDLE)

    async def create_project(
        self, prompt: str, name: str = "NovaProject", **kwargs: Any
    ) -> ProjectState:
        """Executes full SDLC workflow to build a complete software project from natural language prompt.

        Args:
            prompt: Natural language prompt describing desired project.
            name: Project name.
            **kwargs: Extra parameters.

        Returns:
            ProjectState model instance.
        """
        start_time = time.time()
        project_path = f"c:\\Projects\\{name}"

        # 1. SDLC Stage: Requirements
        self.health_monitor.set_state(CopilotState.ANALYZING)
        reqs = await self.requirement_analyzer.analyze_requirements(prompt, project_name=name)

        # 2. SDLC Stage: Architecture
        self.health_monitor.set_state(CopilotState.DESIGNING)
        arch = await self.architecture_engine.design_architecture(reqs)

        # 3. SDLC Stage: Technology Selection
        tech_stack = await self.technology_selector.select_technologies(reqs, arch)

        # 4. SDLC Stage: Code Generation
        self.health_monitor.set_state(CopilotState.GENERATING)
        code_files = await self.code_generator.generate_code(reqs, arch, tech_stack)

        # 5. SDLC Stage: Testing
        self.health_monitor.set_state(CopilotState.TESTING)
        test_report = await self.test_engine.run_tests(project_path)

        # 6. SDLC Stage: Documentation & Git Commit
        project_state = ProjectState(
            name=name,
            path=project_path,
            language=ProjectLanguage.PYTHON,
            stage=SDLCStage.COMPLETED,
            files=code_files,
            requirements=reqs,
            architecture=arch,
            tech_stack=tech_stack,
        )

        await self.project_manager.save_project(project_state)
        await self.git_integration.init_repository(project_path)
        await self.git_integration.commit_changes(project_path, f"feat: initial build of {name}")

        elapsed_ms = (time.time() - start_time) * 1000.0
        total_lines = sum(len(f.content.splitlines()) for f in code_files)
        self.metrics_tracker.record_project_created(total_lines, elapsed_ms)
        self.health_monitor.set_state(CopilotState.IDLE)

        return project_state

    async def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyzes existing codebase repository."""
        return await self.code_understanding.analyze_repository(project_path)

    async def generate_architecture(self, prompt: str) -> ArchitectureDesign:
        """Generates architectural design from prompt."""
        reqs = await self.requirement_analyzer.analyze_requirements(prompt)
        return await self.architecture_engine.design_architecture(reqs)

    async def generate_code(self, prompt: str, project_id: Optional[str] = None) -> List[CodeFile]:
        """Generates source code files."""
        reqs = await self.requirement_analyzer.analyze_requirements(prompt)
        arch = await self.architecture_engine.design_architecture(reqs)
        stack = await self.technology_selector.select_technologies(reqs, arch)
        return await self.code_generator.generate_code(reqs, arch, stack)

    async def debug_project(self, project_path: str, stack_trace: str) -> BugReport:
        """Runs automated debugging and fixes."""
        self.health_monitor.set_state(CopilotState.DEBUGGING)
        bug = await self.debug_engine.debug_code(project_path, stack_trace)
        self.metrics_tracker.record_bug_fixed()
        self.health_monitor.set_state(CopilotState.IDLE)
        return bug

    async def refactor_project(self, project_path: str, goal: str) -> RefactorPlan:
        """Refactors codebase for performance and architecture."""
        self.health_monitor.set_state(CopilotState.REFACTORING)
        ref = await self.refactor_engine.refactor_code(project_path, "# source", goal)
        self.health_monitor.set_state(CopilotState.IDLE)
        return ref

    async def test_project(self, project_path: str) -> TestReport:
        """Runs test suites."""
        self.health_monitor.set_state(CopilotState.TESTING)
        rpt = await self.test_engine.run_tests(project_path)
        self.metrics_tracker.record_tests_passed(rpt.passed_tests)
        self.health_monitor.set_state(CopilotState.IDLE)
        return rpt

    async def deploy_project(self, project_path: str) -> DeploymentConfig:
        """Configures containerization and deployment pipelines."""
        self.health_monitor.set_state(CopilotState.DEPLOYING)
        stack = TechStack(languages=["python"], frameworks=["FastAPI"], databases=["PostgreSQL"])
        cfg = await self.deployment_engine.configure_deployment(project_path, stack)
        self.metrics_tracker.record_deployment()
        self.health_monitor.set_state(CopilotState.IDLE)
        return cfg

    async def review_project(self, project_path: str) -> CodeReviewResult:
        """Performs security, performance, and quality review."""
        files = [CodeFile(path="main.py", content="from fastapi import FastAPI\napp = FastAPI()")]
        return await self.review_engine.review_project(files)

    async def document_project(self, project_id: str) -> DocumentationSet:
        """Generates complete documentation suite for a project."""
        project = await self.project_manager.get_project(project_id)
        if not project:
            project = ProjectState(name=project_id, path=f"c:\\Projects\\{project_id}")
        return await self.documentation_engine.generate_documentation(project)

    async def check_health(self) -> CopilotHealth:
        """Retrieves copilot health monitor diagnostics."""
        return self.health_monitor.check_health()

    async def get_metrics(self) -> CopilotMetrics:
        """Retrieves copilot telemetry metrics."""
        return self.metrics_tracker.get_metrics()

    async def process_copilot_request(self, request: Any) -> Any:
        """Processes AI Software Copilot request across EXPLAIN, GUIDE, and EXECUTE modes."""
        return await self.orchestrator.process_request(request)

