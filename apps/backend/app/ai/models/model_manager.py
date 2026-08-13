"""Model Platform Manager administrative facade for AI Model Integration Platform.
"""

from typing import Optional
from app.ai.models.configuration import ModelPlatformConfiguration
from app.ai.models.interfaces import IModelPlatformManager


class ModelPlatformManager(IModelPlatformManager):
    """High-level administrative manager for AI model platform config and lifecycle."""

    def __init__(self, config: Optional[ModelPlatformConfiguration] = None) -> None:
        self.config = config or ModelPlatformConfiguration()
        self._is_active = True

    @property
    def is_active(self) -> bool:
        """Returns True if platform is active."""
        return self._is_active

    async def start(self) -> None:
        """Starts model platform engine."""
        self._is_active = True
