"""PEP 562 Lazy Import Utility Mapping.
"""

import importlib
from typing import Any

_LAZY_MAP = {
    "WorkflowEngine": "app.ai.workflow.workflow_engine",
    "WorkflowBuilder": "app.ai.workflow.workflow_builder",
    "WorkflowExecutor": "app.ai.workflow.workflow_executor",
    "WorkflowScheduler": "app.ai.workflow.workflow_scheduler",
    "StatePersistence": "app.ai.workflow.state_persistence",
    "CheckpointManager": "app.ai.workflow.checkpoint_manager",
    "RecoveryEngine": "app.ai.workflow.recovery_engine",
    "ApprovalManager": "app.ai.workflow.approval_manager",
    "WorkflowMetricsTracker": "app.ai.workflow.metrics",
    "WorkflowHealthMonitor": "app.ai.workflow.health",
    "Workflow": "app.ai.workflow.models",
    "WorkflowStep": "app.ai.workflow.models",
    "WorkflowState": "app.ai.workflow.models",
    "WorkflowCheckpoint": "app.ai.workflow.models",
    "ApprovalRequest": "app.ai.workflow.models",
    "ApprovalResult": "app.ai.workflow.models"
}

def lazy_import(name: str) -> Any:
    """Dynamically imports a mapped class or utility by name."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"Attribute '{name}' not found in lazy mapping configuration.")
