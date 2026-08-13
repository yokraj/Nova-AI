"""Skill Registry managing skill manifests, status toggles, and metadata tracking.
"""

from typing import Dict, List, Optional
from app.ai.skills.interfaces import ISkillRegistry
from app.ai.skills.models import SkillManifest, SkillMetadata, SkillStatus


class SkillRegistry(ISkillRegistry):
    """Local Skill Registry storing manifests, installation state, and status toggles."""

    def __init__(self) -> None:
        self._registry: Dict[str, SkillMetadata] = {}

    def register_skill(self, manifest: SkillManifest) -> None:
        """Registers skill manifest into registry."""
        meta = SkillMetadata(manifest=manifest, status=SkillStatus.ENABLED)
        self._registry[manifest.skill_id] = meta

    def get_skill(self, skill_id: str) -> Optional[SkillMetadata]:
        """Retrieves metadata by skill_id."""
        return self._registry.get(skill_id)

    def list_skills(self) -> List[SkillMetadata]:
        """Lists all registered skill metadata."""
        return list(self._registry.values())

    def enable_skill(self, skill_id: str) -> bool:
        """Enables target skill."""
        meta = self.get_skill(skill_id)
        if meta:
            meta.status = SkillStatus.ENABLED
            return True
        return False

    def disable_skill(self, skill_id: str) -> bool:
        """Disables target skill."""
        meta = self.get_skill(skill_id)
        if meta:
            meta.status = SkillStatus.DISABLED
            return True
        return False

    def unregister_skill(self, skill_id: str) -> bool:
        """Unregisters skill from registry."""
        if skill_id in self._registry:
            del self._registry[skill_id]
            return True
        return False
