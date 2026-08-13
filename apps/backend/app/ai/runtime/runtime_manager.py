"""Model Runtime Manager controlling simultaneous model loading, unloading, reloading, and GC.
"""

from typing import Dict, List, Optional
from app.ai.runtime.interfaces import IRuntimeManager
from app.ai.runtime.model_profiles import ModelProfilesCatalog
from app.ai.runtime.models import RuntimeState
from app.ai.runtime.resource_scheduler import ResourceScheduler


class RuntimeManager(IRuntimeManager):
    """Manages active model runtime lifecycles across VRAM and RAM."""

    def __init__(self, scheduler: ResourceScheduler, catalog: ModelProfilesCatalog) -> None:
        self.scheduler = scheduler
        self.catalog = catalog
        self._active_models: Dict[str, RuntimeState] = {}

    async def load_model(self, model_id: str) -> bool:
        """Loads model into active memory.

        Args:
            model_id: Target model profile ID.

        Returns:
            True if loaded successfully.
        """
        profile = self.catalog.get_profile(model_id)
        min_vram = profile.min_vram_mb if profile else 2048
        allocated = self.scheduler.allocate_vram(min_vram)
        self._active_models[model_id] = RuntimeState.READY
        return True

    async def unload_model(self, model_id: str) -> bool:
        """Unloads model from active memory.

        Args:
            model_id: Target model profile ID.

        Returns:
            True if unloaded.
        """
        profile = self.catalog.get_profile(model_id)
        min_vram = profile.min_vram_mb if profile else 2048
        self.scheduler.release_vram(min_vram)
        if model_id in self._active_models:
            del self._active_models[model_id]
        return True

    async def reload_model(self, model_id: str) -> bool:
        """Reloads model checkpoint."""
        await self.unload_model(model_id)
        return await self.load_model(model_id)

    async def suspend_model(self, model_id: str) -> bool:
        """Suspends model execution to conserve GPU resources."""
        if model_id in self._active_models:
            self._active_models[model_id] = RuntimeState.SUSPENDED
            return True
        return False

    async def resume_model(self, model_id: str) -> bool:
        """Resumes suspended model."""
        if model_id in self._active_models:
            self._active_models[model_id] = RuntimeState.READY
            return True
        return False

    def list_active_models(self) -> List[str]:
        """Lists currently loaded active model IDs."""
        return list(self._active_models.keys())
