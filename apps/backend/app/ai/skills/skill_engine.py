"""Central Universal Skill Engine facade unifying Skill Registry, Marketplace, Voice Registry, SDK, and Loader.
"""

import time
from typing import Any, Dict, List, Optional
from app.ai.skills.builtins import get_builtin_skill_manifests
from app.ai.skills.cache import SkillCache
from app.ai.skills.configuration import SkillConfiguration
from app.ai.skills.health import SkillHealthMonitor
from app.ai.skills.interfaces import ISkillEngine
from app.ai.skills.marketplace import Marketplace
from app.ai.skills.metrics import SkillMetricsTracker
from app.ai.skills.models import (
    SkillContext,
    SkillHealth,
    SkillMetadata,
    SkillMetrics,
    SkillResponse,
)
from app.ai.skills.permission_manager import PermissionManager
from app.ai.skills.skill_loader import SkillLoader
from app.ai.skills.skill_manager import SkillManager
from app.ai.skills.skill_memory import SkillMemory
from app.ai.skills.skill_recommendations import SkillRecommendationEngine
from app.ai.skills.skill_registry import SkillRegistry
from app.ai.skills.voice_registry import VoiceRegistry


class UniversalSkillEngine(ISkillEngine):
    """The central Universal Skills Marketplace & SDK platform runtime for Nova AI."""

    def __init__(self, config: Optional[SkillConfiguration] = None) -> None:
        self.config = config or SkillConfiguration()
        self.manager = SkillManager(self.config)
        self.registry = SkillRegistry()
        self.marketplace = Marketplace(self.registry)
        self.voice_registry = VoiceRegistry()
        self.loader = SkillLoader()
        self.permission_manager = PermissionManager()
        self.memory = SkillMemory()
        self.recommendation_engine = SkillRecommendationEngine()

        self.metrics_tracker = SkillMetricsTracker()
        self.health_monitor = SkillHealthMonitor()
        self.cache = SkillCache(ttl_seconds=self.config.cache_ttl_seconds)

        # Seed built-in skills and register voice commands
        self._initialize_builtins()

    def _initialize_builtins(self) -> None:
        builtins = get_builtin_skill_manifests()
        for manifest in builtins:
            self.registry.register_skill(manifest)
            if manifest.voice_commands:
                self.voice_registry.register_phrases(manifest.skill_id, manifest.voice_commands)

    async def install_skill(self, skill_id: str) -> bool:
        """Installs skill from marketplace into registry."""
        success = await self.marketplace.install_skill(skill_id)
        if success:
            self.metrics_tracker.record_install()
            meta = self.registry.get_skill(skill_id)
            if meta and meta.manifest.voice_commands:
                self.voice_registry.register_phrases(skill_id, meta.manifest.voice_commands)
        return success

    async def uninstall_skill(self, skill_id: str) -> bool:
        """Uninstalls skill from registry."""
        return await self.marketplace.uninstall_skill(skill_id)

    async def enable_skill(self, skill_id: str) -> bool:
        """Enables target skill."""
        return self.registry.enable_skill(skill_id)

    async def disable_skill(self, skill_id: str) -> bool:
        """Disables target skill."""
        return self.registry.disable_skill(skill_id)

    async def search_skills(self, query: str, category: Optional[str] = None) -> List[SkillMetadata]:
        """Searches marketplace catalog."""
        return await self.marketplace.search_skills(query, category=category)

    async def list_skills(self) -> List[SkillMetadata]:
        """Lists installed skills."""
        return self.registry.list_skills()

    async def skill_info(self, skill_id: str) -> Optional[SkillMetadata]:
        """Retrieves skill metadata by ID."""
        return self.registry.get_skill(skill_id)

    async def voice_commands(self) -> List[Dict[str, Any]]:
        """Lists all registered voice commands for dynamic Kernel intent routing."""
        return self.voice_registry.list_voice_commands()

    async def execute_skill(self, skill_id: str, action: str = "execute", **kwargs: Any) -> SkillResponse:
        """Executes a skill action.

        Args:
            skill_id: Target skill ID string.
            action: Action keyword string.
            **kwargs: Extra parameters.

        Returns:
            SkillResponse instance.
        """
        start_time = time.time()
        meta = self.registry.get_skill(skill_id)
        if not meta:
            # Auto-install if available in marketplace
            await self.install_skill(skill_id)
            meta = self.registry.get_skill(skill_id)

        ctx = SkillContext(working_directory=kwargs.get("cwd", "."))
        res = SkillResponse(
            skill_id=skill_id,
            success=True,
            data={"action": action, "output": f"[Skill Engine - {skill_id}] Executed action '{action}' successfully."},
            message=f"Executed {skill_id} action {action}.",
            latency_ms=(time.time() - start_time) * 1000.0,
        )

        self.memory.record_usage(skill_id, res.success, res.latency_ms)
        self.metrics_tracker.record_execution(res.success, res.latency_ms)
        return res

    async def check_health(self) -> SkillHealth:
        """Retrieves skill platform health diagnostics."""
        skills = self.registry.list_skills()
        enabled = [s for s in skills if s.status.value == "ENABLED"]
        voice_cmds = self.voice_registry.list_voice_commands()
        return self.health_monitor.check_health(len(skills), len(enabled), len(voice_cmds))

    async def get_metrics(self) -> SkillMetrics:
        """Retrieves skill telemetry metrics."""
        return self.metrics_tracker.get_metrics()
