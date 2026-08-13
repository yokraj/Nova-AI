"""Snapshot Manager Module.

Captures, stores, and compares bounded historical telemetry snapshots in memory,
enabling change detection and delta calculations across sampling cycles.
"""

from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
import structlog

logger = structlog.get_logger(__name__)


class SnapshotManager:
    """Manages historical telemetry snapshots ring buffer."""

    def __init__(self, max_retention: int = 50) -> None:
        self.max_retention = max_retention
        self._snapshots: deque = deque(maxlen=max_retention)
        logger.info("snapshot_manager_initialized", max_retention=max_retention)

    def capture_snapshot(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Wraps raw metrics data dictionary into a timestamped snapshot envelope."""
        snapshot = {
            "snapshot_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": metrics_data,
        }
        self.store_snapshot(snapshot)
        return snapshot

    def store_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Appends a snapshot envelope to the historical ring buffer."""
        self._snapshots.append(snapshot)
        logger.debug("snapshot_stored", snapshot_id=snapshot.get("snapshot_id"), count=len(self._snapshots))

    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """Returns the most recent snapshot stored in memory."""
        return self._snapshots[-1] if self._snapshots else None

    def get_previous_snapshot(self) -> Optional[Dict[str, Any]]:
        """Returns the second most recent snapshot stored in memory."""
        if len(self._snapshots) >= 2:
            return self._snapshots[-2]
        return None

    def compare_snapshots(
        self, current: Dict[str, Any], previous: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compares current snapshot with previous snapshot and calculates field deltas."""
        prev = previous or self.get_previous_snapshot()
        if not prev:
            return {"has_changed": True, "changed_fields": list(current.get("data", {}).keys()), "deltas": {}}

        curr_data = current.get("data", {})
        prev_data = prev.get("data", {})

        changed_fields = []
        deltas = {}

        for key, val in curr_data.items():
            prev_val = prev_data.get(key)
            if prev_val != val:
                changed_fields.append(key)
                if isinstance(val, (int, float)) and isinstance(prev_val, (int, float)):
                    deltas[key] = val - prev_val
                else:
                    deltas[key] = val

        return {
            "has_changed": len(changed_fields) > 0,
            "changed_fields": changed_fields,
            "deltas": deltas,
        }

    def cleanup_old_snapshots(self) -> int:
        """Evicts oldest snapshots if retention limit is exceeded."""
        initial_count = len(self._snapshots)
        while len(self._snapshots) > self.max_retention:
            self._snapshots.popleft()
        evicted = initial_count - len(self._snapshots)
        if evicted > 0:
            logger.info("old_snapshots_cleaned_up", evicted=evicted)
        return evicted

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """Returns all snapshots currently stored in memory."""
        return list(self._snapshots)
