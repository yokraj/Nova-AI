"""PEP 562 Lazy Import Utility Mapping for the Services package."""

import importlib
from typing import Any

_LAZY_MAP: dict = {
    # Core Config & Models
    "ServiceConfiguration": "app.ai.services.configuration",
    "ServiceType": "app.ai.services.models",
    "WorkflowState": "app.ai.services.models",
    "ServiceDefinition": "app.ai.services.models",
    "CredentialRecord": "app.ai.services.models",
    "CaptchaInfo": "app.ai.services.models",
    "OTPRequest": "app.ai.services.models",
    "PaymentGuardResult": "app.ai.services.models",
    "ServiceRequest": "app.ai.services.models",
    "ServiceResult": "app.ai.services.models",
    "ServiceMetrics": "app.ai.services.models",
    "ServiceHealth": "app.ai.services.models",
    # Interfaces
    "IServiceRegistry": "app.ai.services.interfaces",
    "IPaymentGuard": "app.ai.services.interfaces",
    "IWorkflowEngine": "app.ai.services.interfaces",
    "IServiceAutomationPlatform": "app.ai.services.interfaces",
    # Exceptions
    "ServiceAutomationError": "app.ai.services.exceptions",
    "WorkflowExecutionError": "app.ai.services.exceptions",
    "AuthenticationFailedError": "app.ai.services.exceptions",
    "CaptchaInterceptionError": "app.ai.services.exceptions",
    "PaymentGuardError": "app.ai.services.exceptions",
    "OTPRequiredError": "app.ai.services.exceptions",
    "ServiceNotFoundError": "app.ai.services.exceptions",
    # Engines & Managers
    "ServiceRegistry": "app.ai.services.service_registry",
    "WorkflowEngine": "app.ai.services.workflow_engine",
    "WebsiteDetector": "app.ai.services.website_detector",
    "AuthenticationManager": "app.ai.services.authentication_manager",
    "CredentialManager": "app.ai.services.credential_manager",
    "SessionManager": "app.ai.services.session_manager",
    "CaptchaDetector": "app.ai.services.captcha_detector",
    "OTPHandler": "app.ai.services.otp_handler",
    "ConfirmationManager": "app.ai.services.confirmation_manager",
    "PaymentGuard": "app.ai.services.payment_guard",
    "WorkflowValidator": "app.ai.services.workflow_validator",
    "WorkflowExecutor": "app.ai.services.workflow_executor",
    "RecoveryManager": "app.ai.services.recovery_manager",
    # Bridges, Telemetry & Providers
    "AutomationBridge": "app.ai.services.automation_bridge",
    "BrowserBridge": "app.ai.services.browser_bridge",
    "LearningBridge": "app.ai.services.learning_bridge",
    "ServiceMetricsTracker": "app.ai.services.metrics",
    "ServiceHealthMonitor": "app.ai.services.health",
    "ServiceCache": "app.ai.services.cache",
    "MockServiceProvider": "app.ai.services.mock_provider",
}


def lazy_import(name: str) -> Any:
    """Dynamically imports a mapped class or utility by name."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"Attribute '{name}' not found in services lazy mapping.")
