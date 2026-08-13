"""Offline Sync providing store-and-forward queue for offline edge node reconnection.
"""

from typing import Any, Dict, List


class OfflineSync:
    """Manages store-and-forward offline execution queue for disconnected nodes."""

    def __init__(self) -> None:
        self._offline_queue: List[Dict[str, Any]] = []

    def queue_offline_task(self, device_id: str, task_payload: Dict[str, Any]) -> None:
        """Queues task payload for store-and-forward sync when device reconnects."""
        self._offline_queue.append({"device_id": device_id, "payload": task_payload})

    def flush_offline_queue(self, device_id: str) -> List[Dict[str, Any]]:
        """Flushes and returns queued tasks for reconnected node."""
        pending = [t for t in self._offline_queue if t["device_id"] == device_id]
        self._offline_queue = [t for t in self._offline_queue if t["device_id"] != device_id]
        return pending
