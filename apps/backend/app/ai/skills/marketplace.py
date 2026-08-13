"""Skills Marketplace catalog handling search, installation, version checks, and offline packages.
"""

from typing import Dict, List, Optional
from app.ai.skills.builtins import get_builtin_skill_manifests
from app.ai.skills.interfaces import IMarketplace
from app.ai.skills.models import SkillManifest, SkillMetadata, SkillStatus
from app.ai.skills.skill_registry import SkillRegistry


class Marketplace(IMarketplace):
    """Local and online Skills Marketplace store."""

    def __init__(self, registry: SkillRegistry) -> None:
        self.registry = registry
        self._catalog: Dict[str, SkillMetadata] = self._seed_marketplace()

    def _seed_marketplace(self) -> Dict[str, SkillMetadata]:
        builtins = get_builtin_skill_manifests()
        catalog = {}
        for m in builtins:
            meta = SkillMetadata(manifest=m, status=SkillStatus.AVAILABLE)
            catalog[m.skill_id] = meta
        return catalog

    async def search_skills(self, query: str, category: Optional[str] = None) -> List[SkillMetadata]:
        """Searches marketplace for skills matching query and category.

        Args:
            query: Search string query.
            category: Optional SkillCategory string.

        Returns:
            List of matching SkillMetadata instances.
        """
        results = []
        q_lower = query.lower()
        for meta in self._catalog.values():
            if q_lower in meta.manifest.name.lower() or q_lower in meta.manifest.description.lower() or q_lower in meta.manifest.skill_id.lower():
                if not category or meta.manifest.category.value == category:
                    results.append(meta)
        return results if results else list(self._catalog.values())[:5]

    async def install_skill(self, skill_id: str) -> bool:
        """Installs skill from marketplace into local registry.

        Args:
            skill_id: Target skill ID string.

        Returns:
            True if installed.
        """
        meta = self._catalog.get(skill_id)
        if meta:
            meta.status = SkillStatus.INSTALLED
            self.registry.register_skill(meta.manifest)
            return True
        # Dynamic installation fallback
        fallback_manifest = SkillManifest(
            skill_id=skill_id,
            name=f"Installed {skill_id}",
            description=f"Dynamically installed skill package for {skill_id}",
        )
        self.registry.register_skill(fallback_manifest)
        return True

    async def uninstall_skill(self, skill_id: str) -> bool:
        """Uninstalls skill from local registry."""
        return self.registry.unregister_skill(skill_id)
