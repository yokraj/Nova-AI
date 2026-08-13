"""Device Registry registering and tracking mesh nodes across OS platforms.
"""

from typing import List, Optional
from app.ai.device_mesh.interfaces import IDeviceRegistry
from app.ai.device_mesh.models import DeviceOSType, MeshNodeDevice, MeshNodeStatus


class DeviceRegistry(IDeviceRegistry):
    """Registers and tracks mesh node devices across OS platforms."""

    def __init__(self) -> None:
        self._devices: List[MeshNodeDevice] = []

    def register_device(self, name: str, os_type: str = "windows", ip_address: str = "127.0.0.1") -> MeshNodeDevice:
        """Registers new node device.

        Args:
            name: Node device name string.
            os_type: DeviceOSType string.
            ip_address: Node IP address string.

        Returns:
            MeshNodeDevice instance.
        """
        ostype = DeviceOSType.WINDOWS
        try:
            ostype = DeviceOSType(os_type.lower())
        except ValueError:
            pass

        device = MeshNodeDevice(name=name, os_type=ostype, ip_address=ip_address, status=MeshNodeStatus.ONLINE)
        self._devices.append(device)
        return device

    def get_device(self, device_id: str) -> Optional[MeshNodeDevice]:
        """Retrieves registered device by ID."""
        for d in self._devices:
            if d.device_id == device_id:
                return d
        return None

    def list_devices(self) -> List[MeshNodeDevice]:
        """Returns list of registered mesh devices."""
        return list(self._devices)
