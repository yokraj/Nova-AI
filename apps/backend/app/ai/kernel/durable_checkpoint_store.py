"""Durable Task Checkpoint Store and Event History Persistence for Nova-AI.

Provides local thread-safe file/SQLite checkpoint persistence, event history audit logging,
and automatic credential/secret redaction to prevent secret leakage in stored task state.
"""

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import copy
import json
import os
import re
import threading
import time
import structlog

logger = structlog.get_logger("durable_checkpoint_store")

# Default local checkpoint storage directory
DEFAULT_CHECKPOINT_DIR = Path.home() / ".nova" / "checkpoints"

# Secret redaction pattern matching sensitive keys
SECRET_KEY_PATTERN = re.compile(r"(\bapi_key\b|\btoken\b|\bauth_token\b|\bpassword\b|\bsecret\b|\bbearer\b|\bcredentials\b|\bprivate_key\b)", re.IGNORECASE)


def redact_secrets(data: Any) -> Any:
    """Recursively redacts secret values matching sensitive key patterns."""
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            if isinstance(key, str) and SECRET_KEY_PATTERN.search(key):
                cleaned[key] = "[REDACTED]"
            else:
                cleaned[key] = redact_secrets(value)
        return cleaned
    elif isinstance(data, list):
        return [redact_secrets(item) for item in data]
    return data


@dataclass
class LongHorizonTaskCheckpoint:
    """Serializable snapshot representing the durable state of a long-horizon task."""

    task_id: str
    user_goal: str
    durable_state: str  # DurableTaskState value string
    current_plan_version: int = 1
    task_graph_dict: Dict[str, Any] = field(default_factory=dict)
    completed_nodes: List[str] = field(default_factory=list)
    running_nodes: List[str] = field(default_factory=list)
    failed_nodes: List[str] = field(default_factory=list)
    waiting_nodes: List[str] = field(default_factory=list)
    blocked_nodes: List[str] = field(default_factory=list)

    # Recovery and metrics counters
    retry_counts: Dict[str, int] = field(default_factory=dict)
    replan_counts: int = 0
    failure_history: List[Dict[str, Any]] = field(default_factory=list)

    # Memory and state snapshots
    working_memory_snapshot: Dict[str, Any] = field(default_factory=dict)
    world_state_references: Dict[str, Any] = field(default_factory=dict)
    verification_status: str = "UNVERIFIED"

    # Budgets
    max_execution_time_sec: float = 3600.0
    max_actions: int = 50
    max_retries: int = 10
    max_replans: int = 3
    max_model_calls: int = 50
    max_estimated_tokens: int = 100000
    deadline_timestamp: Optional[float] = None

    # Current usage counters
    actions_used: int = 0
    retries_used: int = 0
    replans_used: int = 0
    model_calls_used: int = 0
    tokens_used: int = 0
    elapsed_time_sec: float = 0.0

    # Timestamps & Reasons
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    paused_at: Optional[float] = None
    cancelled_at: Optional[float] = None
    pause_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    waiting_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts checkpoint to a dictionary with secrets redacted."""
        raw = asdict(self)
        return redact_secrets(raw)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LongHorizonTaskCheckpoint":
        """Reconstructs checkpoint instance from dictionary data."""
        clean_data = copy.deepcopy(data)
        # Ensure default values for missing keys
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in clean_data.items() if k in valid_keys}
        return cls(**filtered)


class DurableCheckpointStore:
    """Thread-safe persistent disk/JSON file store for task checkpoints and event history."""

    _instance: Optional["DurableCheckpointStore"] = None
    _lock = threading.Lock()

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = Path(storage_dir) if storage_dir else DEFAULT_CHECKPOINT_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir = self.storage_dir / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self._file_lock = threading.Lock()

    @classmethod
    def get_instance(cls, storage_dir: Optional[Path] = None) -> "DurableCheckpointStore":
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(storage_dir=storage_dir)
        return cls._instance

    def save_checkpoint(self, checkpoint: LongHorizonTaskCheckpoint) -> Path:
        """Saves a task checkpoint safely to disk as formatted JSON."""
        checkpoint.updated_at = time.time()
        file_path = self.storage_dir / f"{checkpoint.task_id}.json"
        data = checkpoint.to_dict()

        with self._file_lock:
            temp_path = file_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, file_path)

        logger.info("Saved durable task checkpoint", task_id=checkpoint.task_id, state=checkpoint.durable_state)
        return file_path

    def load_checkpoint(self, task_id: str) -> Optional[LongHorizonTaskCheckpoint]:
        """Loads a task checkpoint from disk."""
        file_path = self.storage_dir / f"{task_id}.json"
        if not file_path.exists():
            logger.debug("Checkpoint file not found", task_id=task_id, path=str(file_path))
            return None

        with self._file_lock:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return LongHorizonTaskCheckpoint.from_dict(data)
            except Exception as e:
                logger.error("Failed to load task checkpoint", task_id=task_id, error=str(e))
                return None

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """Lists metadata summaries for all stored task checkpoints."""
        checkpoints = []
        with self._file_lock:
            for path in self.storage_dir.glob("*.json"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    checkpoints.append({
                        "task_id": data.get("task_id"),
                        "user_goal": data.get("user_goal"),
                        "durable_state": data.get("durable_state"),
                        "plan_version": data.get("current_plan_version"),
                        "updated_at": data.get("updated_at"),
                    })
                except Exception as e:
                    logger.warning("Failed to parse checkpoint summary", path=str(path), error=str(e))
        return checkpoints

    def delete_checkpoint(self, task_id: str) -> bool:
        """Deletes a task checkpoint file from disk."""
        file_path = self.storage_dir / f"{task_id}.json"
        with self._file_lock:
            if file_path.exists():
                file_path.unlink()
                logger.info("Deleted durable task checkpoint", task_id=task_id)
                return True
        return False

    def append_history_event(self, task_id: str, event_type: str, details: Dict[str, Any]) -> None:
        """Appends an immutable event log entry to the task's history audit log."""
        history_path = self.history_dir / f"{task_id}_history.jsonl"
        event = {
            "timestamp": time.time(),
            "task_id": task_id,
            "event_type": event_type,
            "details": redact_secrets(details),
        }
        with self._file_lock:
            with open(history_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")

    def get_task_history(self, task_id: str) -> List[Dict[str, Any]]:
        """Reads and returns the complete event history audit log for a task."""
        history_path = self.history_dir / f"{task_id}_history.jsonl"
        if not history_path.exists():
            return []

        events = []
        with self._file_lock:
            with open(history_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            events.append(json.loads(line))
                        except Exception:
                            continue
        return events
