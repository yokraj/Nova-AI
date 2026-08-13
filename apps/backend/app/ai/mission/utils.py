"""PEP 562 Lazy Import Utility Mapping.
"""

import importlib
from typing import Any

_LAZY_MAP = {
    "MissionEngine": "app.ai.mission.mission_engine",
    "MissionManager": "app.ai.mission.mission_manager",
    "MissionQueue": "app.ai.mission.mission_queue",
    "MissionScheduler": "app.ai.mission.mission_scheduler",
    "MissionExecutor": "app.ai.mission.mission_executor",
    "MissionStateMachine": "app.ai.mission.mission_state",
    "MissionContextContainer": "app.ai.mission.mission_context",
    "CheckpointManager": "app.ai.mission.checkpoint_manager",
    "RecoveryManager": "app.ai.mission.recovery_manager",
    "AutonomousDecisionEngine": "app.ai.mission.autonomous_decision_engine",
    "MissionMonitor": "app.ai.mission.mission_monitor",
    "ProgressTracker": "app.ai.mission.progress_tracker",
    "NotificationManager": "app.ai.mission.notification_manager",
    "MissionMetricsTracker": "app.ai.mission.metrics",
    "MissionHealthMonitor": "app.ai.mission.health",
    "Mission": "app.ai.mission.models",
    "MissionState": "app.ai.mission.models",
    "MissionContext": "app.ai.mission.models",
    "MissionCheckpoint": "app.ai.mission.models",
    "ProgressReport": "app.ai.mission.models"
}

def lazy_import(name: str) -> Any:
    """Dynamically imports a mapped class or utility by name."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"Attribute '{name}' not found in lazy mapping configuration.")
