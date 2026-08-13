"""Abstract BaseSkill class for Nova Skill SDK implementations with runtime AI injection.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine
from app.ai.skills.models import SkillContext, SkillManifest, SkillResponse


class BaseSkill(ABC):
    """Abstract base class that all Nova skills inherit from with AI runtime injection."""

    def __init__(self, manifest: SkillManifest, runtime_engine: Optional[UniversalAIRuntimeEngine] = None) -> None:
        self.manifest = manifest
        self.runtime = runtime_engine or UniversalAIRuntimeEngine()

    @property
    def skill_id(self) -> str:
        return self.manifest.skill_id

    @property
    def name(self) -> str:
        return self.manifest.name

    async def chat(self, prompt: str, **kwargs: Any) -> Any:
        """Invokes chat via UniversalAIRuntimeEngine."""
        return await self.runtime.chat(prompt, **kwargs)

    async def code(self, prompt: str, **kwargs: Any) -> Any:
        """Invokes code generation via UniversalAIRuntimeEngine."""
        return await self.runtime.code(prompt, **kwargs)

    async def reason(self, prompt: str, **kwargs: Any) -> Any:
        """Invokes reasoning via UniversalAIRuntimeEngine."""
        return await self.runtime.reason(prompt, **kwargs)

    @abstractmethod
    async def execute(self, action: str, context: SkillContext, **kwargs: Any) -> SkillResponse:
        """Executes skill action payload.

        Args:
            action: Action keyword name string.
            context: SkillContext payload.
            **kwargs: Extra parameters.

        Returns:
            SkillResponse instance.
        """
        pass
