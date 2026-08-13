"""Autonomous Long-Running Mission & Workflow Engine package.

Exposes configuration, models, interfaces, exceptions, mission manager, workflow engine, task scheduler,
checkpoint engine, recovery engine, approval queue, background workers, progress engine, notification engine,
dashboard API, workflow recorder, mission memory, observability, and central MissionRuntimeEngine.
"""

import sys
from typing import Any
from app.ai.mission_runtime.utils import lazy_import

__all__ = [
    "MissionRuntimeConfiguration",
    "MissionState",
    "WorkflowType",
    "MissionPriority",
    "WorkerStatus",
    "TaskItem",
    "WorkflowDefinition",
    "CheckpointData",
    "RecoveryRecord",
    "ApprovalItem",
    "ProgressReport",
    "NotificationMessage",
    "WorkflowTemplate",
    "MissionRecord",
    "MissionMetrics",
    "MissionHealth",
    "IMissionRuntimeEngine",
    "IMissionManager",
    "IWorkflowEngine",
    "ITaskScheduler",
    "ICheckpointEngine",
    "IRecoveryEngine",
    "IApprovalQueue",
    "IBackgroundWorkers",
    "IProgressEngine",
    "INotificationEngine",
    "IDashboardAPI",
    "IWorkflowRecorder",
    "IMissionMemory",
    "IRuntimeManager",
    "MissionRuntimeError",
    "MissionManager",
    "WorkflowEngine",
    "TaskScheduler",
    "CheckpointEngine",
    "RecoveryEngine",
    "ApprovalQueue",
    "BackgroundWorkers",
    "ProgressEngine",
    "NotificationEngine",
    "DashboardAPI",
    "WorkflowRecorder",
    "MissionMemory",
    "MissionMetricsTracker",
    "MissionHealthMonitor",
    "MissionCache",
    "MockMissionRuntimeProvider",
    "MissionRuntimeManager",
    "MissionRuntimeEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
