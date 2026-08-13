"""Device Profiles profiling hardware specifications, OS features, and GPU capabilities.
"""

from typing import Any, Dict


class DeviceProfiles:
    """Profiles hardware capabilities including GPU compute capability and VRAM capacity."""

    def get_profile(self, os_type: str) -> Dict[str, Any]:
        """Returns standard profile capabilities for specified OS type."""
        return {
            "os_type": os_type,
            "supports_cuda": os_type in ("windows", "linux", "wsl", "docker"),
            "supports_docker": os_type in ("linux", "wsl", "windows", "cloud_vm"),
            "has_npu": os_type in ("windows", "android"),
        }
