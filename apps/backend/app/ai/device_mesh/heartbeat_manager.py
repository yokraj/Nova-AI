"""Heartbeat Manager tracking high-frequency node heartbeat signals.
"""

import time
from typing import Dict


class HeartbeatManager:
    """Tracks node heartbeat timestamps to detect dead or disconnected nodes."""

    def __init__(self) -> None:
        self._last_heartbeats: Dict[str, float] = {}

    def record_heartbeat(self, device_id: str) -> None:
        """Records node heartbeat signal timestamp."""
        self._last_heartbeats[device_id] = time.time()

    def is_alive(self, device_id: str, timeout_sec: float = 15.0) -> bool:
        """Returns True if node heartbeat was received within timeout_sec."""
        if device_id in self._last_heartbeats:
            return time.time() - self._last_heartbeats[device_id] <= timeout_sec
        return True
