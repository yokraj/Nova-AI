"""AI Software Copilot package.

Exposes copilot configuration, models, interfaces, exceptions, requirement analyzer,
architecture engine, technology selector, code generator, code understanding engine, debug engine,
refactor engine, test engine, devops engine, documentation engine, review engine, project manager,
IDE/Git integrations, observability, and central CopilotEngine.
"""

import sys
from typing import Any
from app.ai.copilot.utils import lazy_import

__all__ = [
    "CopilotConfiguration",
    "ProjectLanguage",
    "ArchitectureStyle",
    "SDLCStage",
    "CopilotState",
    "RequirementDocument",
    "ArchitectureDesign",
    "TechStack",
    "CodeFile",
    "ProjectState",
    "BugReport",
    "RefactorPlan",
    "TestReport",
    "DeploymentConfig",
    "CodeReviewResult",
    "DocumentationSet",
    "CopilotMetrics",
    "CopilotHealth",
    "ICopilotEngine",
    "IRequirementAnalyzer",
    "ISoftwareArchitectureEngine",
    "ITechnologySelector",
    "ICodeGenerator",
    "ICodeUnderstandingEngine",
    "IDebugEngine",
    "IRefactorEngine",
    "ITestEngine",
    "IDevOpsEngine",
    "IDocumentationEngine",
    "ICodeReviewEngine",
    "IProjectManager",
    "ICopilotManager",
    "CopilotError",
    "RequirementAnalyzer",
    "SoftwareArchitectureEngine",
    "TechnologySelector",
    "CodeGenerator",
    "CodeUnderstandingEngine",
    "DebugEngine",
    "RefactorEngine",
    "TestEngine",
    "DevOpsEngine",
    "DocumentationEngine",
    "CodeReviewEngine",
    "ProjectManager",
    "IDEIntegration",
    "GitIntegration",
    "CopilotMetricsTracker",
    "CopilotHealthMonitor",
    "CopilotCache",
    "MockCopilotProvider",
    "CopilotManager",
    "CopilotEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
