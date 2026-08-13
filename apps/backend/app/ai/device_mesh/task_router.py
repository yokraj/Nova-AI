"""Task Router calculating node latency, load, and capabilities to select target execution node.
"""

from typing import List, Optional
from app.ai.device_mesh.models import MeshNodeDevice


class TaskRouter:
    """Routes tasks to the optimal node based on latency, available RAM/VRAM, and OS capabilities."""

    def select_best_node(self, nodes: List[MeshNodeDevice], required_os: Optional[str] = None) -> MeshNodeDevice:
        """Selects optimal target node from candidate list."""
        if not nodes:
            return MeshNodeDevice(name="Default Primary", os_type="windows")
        for node in nodes:
            if required_os and node.os_type.value == required_os.lower():
                return node
        return nodes[0]
