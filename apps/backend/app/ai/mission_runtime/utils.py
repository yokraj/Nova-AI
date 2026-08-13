"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.mission_runtime.
"""

import importlib
from typing import Any, Dict, List

_LAZY_MAP: Dict[str, str] = {
    "MissionRuntimeConfiguration": "app.ai.mission_runtime.configuration",
    "MissionState": "app.ai.mission_runtime.models",
    "WorkflowType": "app.ai.mission_runtime.models",
    "MissionPriority": "app.ai.mission_runtime.models",
    "WorkerStatus": "app.ai.mission_runtime.models",
    "TaskItem": "app.ai.mission_runtime.models",
    "WorkflowDefinition": "app.ai.mission_runtime.models",
    "CheckpointData": "app.ai.mission_runtime.models",
    "RecoveryRecord": "app.ai.mission_runtime.models",
    "ApprovalItem": "app.ai.mission_runtime.models",
    "ProgressReport": "app.ai.mission_runtime.models",
    "NotificationMessage": "app.ai.mission_runtime.models",
    "WorkflowTemplate": "app.ai.mission_runtime.models",
    "MissionRecord": "app.ai.mission_runtime.models",
    "MissionMetrics": "app.ai.mission_runtime.models",
    "MissionHealth": "app.ai.mission_runtime.models",
    "IMissionRuntimeEngine": "app.ai.mission_runtime.interfaces",
    "IMissionManager": "app.ai.mission_runtime.interfaces",
    "IWorkflowEngine": "app.ai.mission_runtime.interfaces",
    "ITaskScheduler": "app.ai.mission_runtime.interfaces",
    "ICheckpointEngine": "app.ai.mission_runtime.interfaces",
    "IRecoveryEngine": "app.ai.mission_runtime.interfaces",
    "IApprovalQueue": "app.ai.mission_runtime.interfaces",
    "IBackgroundWorkers": "app.ai.mission_runtime.interfaces",
    "IProgressEngine": "app.ai.mission_runtime.interfaces",
    "INotificationEngine": "app.ai.mission_runtime.interfaces",
    "IDashboardAPI": "app.ai.mission_runtime.interfaces",
    "IWorkflowRecorder": "app.ai.mission_runtime.interfaces",
    "IMissionMemory": "app.ai.mission_runtime.interfaces",
    "IRuntimeManager": "app.ai.mission_runtime.interfaces",
    "MissionRuntimeError": "app.ai.mission_runtime.exceptions",
    "MissionManager": "app.ai.mission_runtime.mission_manager",
    "WorkflowEngine": "app.ai.mission_runtime.workflow_engine",
    "TaskScheduler": "app.ai.mission_runtime.task_scheduler",
    "CheckpointEngine": "app.ai.mission_runtime.checkpoint_engine",
    "RecoveryEngine": "app.ai.mission_runtime.recovery_engine",
    "ApprovalQueue": "app.ai.mission_runtime.approval_queue",
    "BackgroundWorkers": "app.ai.mission_runtime.background_workers",
    "ProgressEngine": "app.ai.mission_runtime.progress_engine",
    "NotificationEngine": "app.ai.mission_runtime.notification_engine",
    "DashboardAPI": "app.ai.mission_runtime.dashboard_api",
    "WorkflowRecorder": "app.ai.mission_runtime.workflow_recorder",
    "MissionMemory": "app.ai.mission_runtime.mission_memory",
    "MissionMetricsTracker": "app.ai.mission_runtime.metrics",
    "MissionHealthMonitor": "app.ai.mission_runtime.health",
    "MissionCache": "app.ai.mission_runtime.cache",
    "MockMissionRuntimeProvider": "app.ai.mission_runtime.mock_provider",
    "MissionRuntimeManager": "app.ai.mission_runtime.runtime_manager",
    "MissionRuntimeEngine": "app.ai.mission_runtime.runtime_engine",
}


def lazy_import(name: str) -> Any:
    """Lazy imports a symbol based on the module map.

    Args:
        name: Name of symbol to import.

    Returns:
        The imported symbol object.
    """
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"module 'app.ai.mission_runtime' has no attribute '{name}'")


def calculate_eta(completed_count: int, total_count: int, elapsed_seconds: float) -> float:
    """Calculates estimated time remaining in seconds.

    Args:
        completed_count: Tasks finished.
        total_count: Total tasks in workflow.
        elapsed_seconds: Seconds elapsed so far.

    Returns:
        Estimated remaining time in seconds.
    """
    if completed_count == 0 or total_count <= completed_count:
        return 0.0
    avg_per_task = elapsed_seconds / completed_count
    remaining_tasks = total_count - completed_count
    return float(avg_per_task * remaining_tasks)
