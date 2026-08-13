"""Central AutonomousSoftwareCompanyEngine facade for Nova Autonomous AI Software Engineering Company.
"""

from typing import Any, Dict, Optional
from app.ai.software_company.interfaces import IAutonomousSoftwareCompanyEngine
from app.ai.software_company.manager import AutonomousSoftwareCompanyManager
from app.ai.software_company.models import CompanyHealth, ProjectBuildResult


class AutonomousSoftwareCompanyEngine(IAutonomousSoftwareCompanyEngine):
    """Central Software Company facade acting as the end-to-end software factory brain for Nova AI OS."""

    _instance: Optional["AutonomousSoftwareCompanyEngine"] = None

    def __new__(cls, manager: Optional[AutonomousSoftwareCompanyManager] = None) -> "AutonomousSoftwareCompanyEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.manager = manager or AutonomousSoftwareCompanyManager()
        elif manager is not None:
            cls._instance.manager = manager
        return cls._instance

    async def build_software(self, prompt: str) -> ProjectBuildResult:
        """Builds complete production-grade software project from prompt."""
        res = await self.manager.factory_engine.build_project(prompt)
        self.manager.project_memory.store_memory(res.project_id, "build_result", res.model_dump(mode="json"))
        return res

    async def process_voice_build_command(self, voice_prompt: str) -> Dict[str, Any]:
        """Processes voice command to trigger full software factory build."""
        return await self.manager.voice_company.process_voice_project_request(voice_prompt)

    def get_company_health(self) -> CompanyHealth:
        """Snapshot company health metrics."""
        return self.manager.get_health()
