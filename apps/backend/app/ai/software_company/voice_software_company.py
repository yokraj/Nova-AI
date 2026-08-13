"""Voice-Driven Software Company Orchestrator.
"""

from typing import Any, Dict
from app.ai.software_company.interfaces import IVoiceSoftwareCompany
from app.ai.software_company.project_factory import ProjectFactoryEngine


class VoiceSoftwareCompany(IVoiceSoftwareCompany):
    """Maps natural voice requests ("Nova, build an ERP system") to multi-team software factory execution."""

    def __init__(self, factory_engine: ProjectFactoryEngine) -> None:
        self.factory_engine = factory_engine

    async def process_voice_project_request(self, voice_prompt: str) -> Dict[str, Any]:
        """Executes full software factory build from voice request."""
        build_result = await self.factory_engine.build_project(voice_prompt)
        return {
            "voice_prompt": voice_prompt,
            "project_id": build_result.project_id,
            "title": build_result.title,
            "status": build_result.status.value,
            "stage": build_result.stage.value,
            "generated_files": build_result.generated_files_count,
            "test_coverage_percent": build_result.test_coverage_percent,
            "deployment_url": build_result.deployment_url,
            "documentation_path": build_result.documentation_path,
        }
