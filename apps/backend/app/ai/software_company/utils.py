"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.software_company.
"""

import importlib
from typing import Any, Dict

_LAZY_MAP: Dict[str, str] = {
    "SoftwareCompanyConfiguration": "app.ai.software_company.configuration",
    "ProjectStage": "app.ai.software_company.models",
    "BuildStatus": "app.ai.software_company.models",
    "SoftwareProjectSpec": "app.ai.software_company.models",
    "SoftwareArchitectureBlueprint": "app.ai.software_company.models",
    "DBSchemaSpec": "app.ai.software_company.models",
    "APIEndpointSpec": "app.ai.software_company.models",
    "ProjectBuildResult": "app.ai.software_company.models",
    "ProjectMemoryItem": "app.ai.software_company.models",
    "ProjectDashboardStatus": "app.ai.software_company.models",
    "CompanyHealth": "app.ai.software_company.models",
    "IProjectRequirementsDivision": "app.ai.software_company.interfaces",
    "ISystemArchitectureDivision": "app.ai.software_company.interfaces",
    "IProjectFactoryEngine": "app.ai.software_company.interfaces",
    "IContinuousProjectMemory": "app.ai.software_company.interfaces",
    "IVoiceSoftwareCompany": "app.ai.software_company.interfaces",
    "IAutonomousSoftwareCompanyEngine": "app.ai.software_company.interfaces",
    "SoftwareCompanyError": "app.ai.software_company.exceptions",
    "ArchitectureValidationError": "app.ai.software_company.exceptions",
    "BuildPipelineFailedError": "app.ai.software_company.exceptions",
    "AutoFixMaxRetriesExceededError": "app.ai.software_company.exceptions",
    "ProjectFactoryEngine": "app.ai.software_company.project_factory",
    "ContinuousProjectMemory": "app.ai.software_company.project_memory",
    "VoiceSoftwareCompany": "app.ai.software_company.voice_software_company",
    "SoftwareDashboardRuntime": "app.ai.software_company.dashboard_runtime",
    "AutonomousSoftwareCompanyManager": "app.ai.software_company.manager",
    "AutonomousSoftwareCompanyEngine": "app.ai.software_company.engine",
}


def lazy_import(name: str) -> Any:
    """Dynamically imports symbol via PEP 562 lazy mapping."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
