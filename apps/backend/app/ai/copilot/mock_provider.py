"""Mock Copilot Provider for offline unit tests and CI integration.
"""

from typing import Any, Dict, List, Optional
from app.ai.copilot.models import (
    ArchitectureDesign,
    ArchitectureStyle,
    BugReport,
    CodeFile,
    CodeReviewResult,
    CopilotHealth,
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


class MockCopilotProvider:
    """Mock Copilot Provider returning deterministic test data."""

    async def create_project(self, prompt: str, name: str = "MockProject", **kwargs: Any) -> ProjectState:
        """Returns mock ProjectState."""
        return ProjectState(
            name=name,
            path=f"c:\\Projects\\{name}",
            language=ProjectLanguage.PYTHON,
            stage=SDLCStage.COMPLETED,
            files=[
                CodeFile(path="apps/backend/main.py", content="# Mock main", language="python"),
                CodeFile(path="Dockerfile", content="# Mock Dockerfile", language="dockerfile"),
            ],
            requirements=RequirementDocument(project_name=name, functional_requirements=[prompt]),
            architecture=ArchitectureDesign(style=ArchitectureStyle.MODULAR_MONOLITH),
            tech_stack=TechStack(languages=["python"], frameworks=["FastAPI"]),
        )

    async def check_health(self) -> CopilotHealth:
        """Returns mock CopilotHealth."""
        return CopilotHealth(
            is_healthy=True,
            copilot_state=CopilotState.IDLE,
            active_projects_count=1,
            loaded_engines=["MockEngine"],
        )
