"""Mock Skill Provider returning deterministic test responses for offline tests and CI.
"""

from typing import Any, List, Optional
from app.ai.skills.models import SkillCategory, SkillManifest, SkillMetadata, SkillResponse, SkillStatus, VoiceCommandPhrase


class MockSkillProvider:
    """Mock Skill Provider returning deterministic test responses."""

    async def mock_list_skills(self) -> List[SkillMetadata]:
        m = SkillManifest(
            skill_id="mock_skill_01",
            name="Mock Test Skill",
            category=SkillCategory.UTILITIES,
            description="Mock Skill for offline test suite.",
            voice_commands=[VoiceCommandPhrase(phrase="Mock action", aliases=["Run mock"])],
        )
        return [SkillMetadata(manifest=m, status=SkillStatus.ENABLED)]

    async def mock_execute(self, skill_id: str) -> SkillResponse:
        return SkillResponse(
            skill_id=skill_id,
            success=True,
            data={"result": "mock_execution_output"},
            message=f"Mock skill {skill_id} executed successfully.",
        )
