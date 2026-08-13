"""PEP 562 Lazy Import Utility Mapping for the Execution package."""

import importlib
from typing import Any

_LAZY_MAP: dict = {
    # Core
    "ExecutionConfiguration": "app.ai.execution.configuration",
    # Models
    "ExecutionState": "app.ai.execution.models",
    "StepStatus": "app.ai.execution.models",
    "PriorityLevel": "app.ai.execution.models",
    "ExecutionStep": "app.ai.execution.models",
    "MissionExecutionPlan": "app.ai.execution.models",
    "CheckpointData": "app.ai.execution.models",
    "TransactionRecord": "app.ai.execution.models",
    "ResourceSnapshot": "app.ai.execution.models",
    "ExecutionMetrics": "app.ai.execution.models",
    "ExecutionHealth": "app.ai.execution.models",
    # Interfaces
    "IExecutionRuntime": "app.ai.execution.interfaces",
    "IMissionExecutor": "app.ai.execution.interfaces",
    "IPluginExecutor": "app.ai.execution.interfaces",
    "ITransactionManager": "app.ai.execution.interfaces",
    "ICheckpointManager": "app.ai.execution.interfaces",
    # Exceptions
    "ExecutionError": "app.ai.execution.exceptions",
    "TaskExecutionError": "app.ai.execution.exceptions",
    "StepFailedError": "app.ai.execution.exceptions",
    "ApprovalRequiredError": "app.ai.execution.exceptions",
    "RollbackError": "app.ai.execution.exceptions",
    "CheckpointError": "app.ai.execution.exceptions",
    "ResourceExhaustedError": "app.ai.execution.exceptions",
    # Sub-systems
    "ExecutionContext": "app.ai.execution.execution_context",
    "StateManager": "app.ai.execution.state_manager",
    "ExecutionQueue": "app.ai.execution.execution_queue",
    "ExecutionScheduler": "app.ai.execution.execution_scheduler",
    "ResourceManager": "app.ai.execution.resource_manager",
    "CheckpointManager": "app.ai.execution.checkpoint_manager",
    "RollbackManager": "app.ai.execution.rollback_manager",
    "TransactionManager": "app.ai.execution.transaction_manager",
    "RecoveryManager": "app.ai.execution.recovery_manager",
    "ApprovalHandler": "app.ai.execution.approval_handler",
    "PluginExecutor": "app.ai.execution.plugin_executor",
    "MissionExecutor": "app.ai.execution.mission_executor",
    "ExecutionPipeline": "app.ai.execution.execution_pipeline",
    "ProgressTracker": "app.ai.execution.progress_tracker",
    "ExecutionMonitor": "app.ai.execution.execution_monitor",
    "ExecutionEventPublisher": "app.ai.execution.event_publisher",
    "StatusManager": "app.ai.execution.status_manager",
    "AuditLogger": "app.ai.execution.audit_logger",
    "ExecutionMetricsTracker": "app.ai.execution.metrics",
    "ExecutionHealthMonitor": "app.ai.execution.health",
    "ExecutionCache": "app.ai.execution.cache",
    "ExecutionRuntime": "app.ai.execution.execution_runtime",
    "MockExecutionProvider": "app.ai.execution.mock_provider",
}


def lazy_import(name: str) -> Any:
    """Dynamically imports a mapped class or utility by name."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"Attribute '{name}' not found in execution lazy mapping.")
