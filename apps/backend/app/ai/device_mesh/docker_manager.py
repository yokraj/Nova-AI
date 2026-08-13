"""Docker Manager managing Docker containers and images across mesh nodes.
"""

from typing import Any, Dict, List


class DockerManager:
    """Manages Docker engine, containers, and image pulls across mesh nodes."""

    def list_containers(self, device_id: str) -> List[Dict[str, Any]]:
        """Returns active Docker containers on node."""
        return [
            {"container_id": "c_nova_backend", "image": "nova/backend:latest", "status": "running"},
        ]
