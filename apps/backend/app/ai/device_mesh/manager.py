"""Subsystem Manager facade for Device Mesh platform configuration and lifecycle.
"""

from typing import Optional
from app.ai.device_mesh.configuration import DeviceMeshConfiguration
from app.ai.device_mesh.interfaces import IDeviceMeshManagerFacade


class DeviceMeshManagerFacade(IDeviceMeshManagerFacade):
    """High-level administrative manager for device mesh platform configuration and lifecycle."""

    def __init__(self, config: Optional[DeviceMeshConfiguration] = None) -> None:
        self.config = config or DeviceMeshConfiguration()
        self._is_active = True

    @property
    def is_active(self) -> bool:
        """Returns True if device mesh manager facade is active."""
        return self._is_active

    async def start(self) -> None:
        """Starts device mesh manager."""
        self._is_active = True
