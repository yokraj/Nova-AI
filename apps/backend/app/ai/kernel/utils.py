"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.kernel.
"""

import importlib
from typing import Any, Dict, List

_LAZY_MAP: Dict[str, str] = {
    "KernelConfiguration": "app.ai.kernel.configuration",
    "KernelState": "app.ai.kernel.models",
    "OperatingMode": "app.ai.kernel.models",
    "PriorityLevel": "app.ai.kernel.models",
    "IntentRequest": "app.ai.kernel.models",
    "IntentResponse": "app.ai.kernel.models",
    "ExecutionContext": "app.ai.kernel.models",
    "SystemSnapshot": "app.ai.kernel.models",
    "CapabilityMatch": "app.ai.kernel.models",
    "ExecutionPlan": "app.ai.kernel.models",
    "PlanNode": "app.ai.kernel.models",
    "VerificationResult": "app.ai.kernel.models",
    "EventRecord": "app.ai.kernel.models",
    "OSMemoryState": "app.ai.kernel.models",
    "KernelMetrics": "app.ai.kernel.models",
    "KernelHealth": "app.ai.kernel.models",
    "IKernelEngine": "app.ai.kernel.interfaces",
    "IIntentEngine": "app.ai.kernel.interfaces",
    "ICapabilityResolver": "app.ai.kernel.interfaces",
    "IDynamicPlanner": "app.ai.kernel.interfaces",
    "IResourceManager": "app.ai.kernel.interfaces",
    "IContextEngine": "app.ai.kernel.interfaces",
    "IRuntimeCoordinator": "app.ai.kernel.interfaces",
    "IUniversalVerifier": "app.ai.kernel.interfaces",
    "IEventBus": "app.ai.kernel.interfaces",
    "IOSMemory": "app.ai.kernel.interfaces",
    "ICopilotIntegration": "app.ai.kernel.interfaces",
    "IVoiceOrchestrator": "app.ai.kernel.interfaces",
    "ISecurityGuard": "app.ai.kernel.interfaces",
    "IKernelManager": "app.ai.kernel.interfaces",
    "KernelError": "app.ai.kernel.exceptions",
    "IntentEngine": "app.ai.kernel.intent_engine",
    "CapabilityResolver": "app.ai.kernel.capability_resolver",
    "DynamicPlanner": "app.ai.kernel.dynamic_planner",
    "SystemResourceManager": "app.ai.kernel.resource_manager",
    "ContextEngine": "app.ai.kernel.context_engine",
    "RuntimeCoordinator": "app.ai.kernel.runtime_coordinator",
    "UniversalVerifier": "app.ai.kernel.universal_verifier",
    "EventBus": "app.ai.kernel.event_bus",
    "OSMemory": "app.ai.kernel.os_memory",
    "CopilotIntegration": "app.ai.kernel.copilot_integration",
    "VoiceOrchestrator": "app.ai.kernel.voice_orchestrator",
    "KernelSecurityGuard": "app.ai.kernel.kernel_security",
    "KernelMetricsTracker": "app.ai.kernel.metrics",
    "KernelHealthMonitor": "app.ai.kernel.health",
    "KernelCache": "app.ai.kernel.cache",
    "MockKernelProvider": "app.ai.kernel.mock_provider",
    "KernelManager": "app.ai.kernel.kernel_manager",
    "KernelEngine": "app.ai.kernel.kernel_engine",
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
    raise AttributeError(f"module 'app.ai.kernel' has no attribute '{name}'")


def format_voice_response(goal: str, status: str, details: str = "") -> str:
    """Formats natural spoken text for voice-first response.

    Args:
        goal: The goal executed.
        status: Status string.
        details: Additional details.

    Returns:
        Spoken string response.
    """
    if status.lower() == "completed" or status.lower() == "success":
        return f"Successfully completed request: {goal}. {details}".strip()
    elif status.lower() == "approval_required":
        return f"Request to {goal} requires your approval before proceeding."
    else:
        return f"I encountered an issue processing request: {goal}. {details}".strip()
