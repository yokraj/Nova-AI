"""PEP 562 Lazy Import Utility Mapping.
"""

import importlib
from typing import Any

_LAZY_MAP = {
    "SafetyEngine": "app.ai.safety.safety_engine",
    "ApprovalManager": "app.ai.safety.approval_manager",
    "ApprovalQueue": "app.ai.safety.approval_queue",
    "ApprovalHistory": "app.ai.safety.approval_history",
    "ApprovalContext": "app.ai.safety.approval_context",
    "PermissionManager": "app.ai.safety.permission_manager",
    "ConsentManager": "app.ai.safety.consent_manager",
    "RiskClassifier": "app.ai.safety.risk_classifier",
    "PolicyEngine": "app.ai.safety.policy_engine",
    "ActionValidator": "app.ai.safety.action_validator",
    "ConfirmationManager": "app.ai.safety.confirmation_manager",
    "AuditLogger": "app.ai.safety.audit_logger",
    "NotificationManager": "app.ai.safety.notification_manager",
    "SafetyMetricsTracker": "app.ai.safety.metrics",
    "SafetyHealthMonitor": "app.ai.safety.health",
    "RiskLevel": "app.ai.safety.models",
    "RiskAssessment": "app.ai.safety.models",
    "ApprovalItem": "app.ai.safety.models",
    "UserConsent": "app.ai.safety.models",
    "AuditRecord": "app.ai.safety.models"
}

def lazy_import(name: str) -> Any:
    """Dynamically imports a mapped class or utility by name."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"Attribute '{name}' not found in lazy mapping configuration.")
