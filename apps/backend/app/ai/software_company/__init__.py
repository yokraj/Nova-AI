"""Autonomous AI Software Engineering Company & End-to-End Project Factory package.

Exposes configuration, models, interfaces, exceptions, project factory pipeline, continuous project memory,
voice software company, software dashboard runtime, manager, and central AutonomousSoftwareCompanyEngine facade.
"""

from typing import Any
from app.ai.software_company.utils import lazy_import

__all__ = [
    "SoftwareCompanyConfiguration",
    "ProjectStage",
    "BuildStatus",
    "SoftwareProjectSpec",
    "SoftwareArchitectureBlueprint",
    "DBSchemaSpec",
    "APIEndpointSpec",
    "ProjectBuildResult",
    "ProjectMemoryItem",
    "ProjectDashboardStatus",
    "CompanyHealth",
    "IProjectRequirementsDivision",
    "ISystemArchitectureDivision",
    "IProjectFactoryEngine",
    "IContinuousProjectMemory",
    "IVoiceSoftwareCompany",
    "IAutonomousSoftwareCompanyEngine",
    "SoftwareCompanyError",
    "ArchitectureValidationError",
    "BuildPipelineFailedError",
    "AutoFixMaxRetriesExceededError",
    "ProjectFactoryEngine",
    "ContinuousProjectMemory",
    "VoiceSoftwareCompany",
    "SoftwareDashboardRuntime",
    "AutonomousSoftwareCompanyManager",
    "AutonomousSoftwareCompanyEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
