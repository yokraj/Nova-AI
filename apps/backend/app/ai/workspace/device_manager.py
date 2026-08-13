"""Device Manager registering remote Nova nodes, desktop PCs, laptops, and cloud workers.
"""

from typing import List
from app.ai.workspace.models import DeviceStatus, WorkspaceDevice


class DeviceManager:
    """Registers remote node devices and tracks online statuses."""

    def register_device(self, name: str, ip_address: str, device_type: str = "desktop_pc") -> WorkspaceDevice:
        """Registers new remote node device."""
        return WorkspaceDevice(
            name=name,
            ip_address=ip_address,
            device_type=device_type,
            status=DeviceStatus.ONLINE,
        )
