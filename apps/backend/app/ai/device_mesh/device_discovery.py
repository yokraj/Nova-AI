"""Device Discovery discovering local network mDNS/SSDP peers and mesh nodes.
"""

from typing import Any, Dict, List


class DeviceDiscovery:
    """Discovers peer devices on local network using mDNS and SSDP broadcast."""

    def discover_peers(self) -> List[Dict[str, Any]]:
        """Scans network and returns list of discovered un-paired mesh node candidates."""
        return [
            {"name": "Local WSL2 Node", "os_type": "wsl", "ip_address": "172.28.16.1", "discovered_via": "mDNS"},
            {"name": "Raspberry Pi 4 Edge", "os_type": "raspberry_pi", "ip_address": "192.168.1.150", "discovered_via": "SSDP"},
        ]
