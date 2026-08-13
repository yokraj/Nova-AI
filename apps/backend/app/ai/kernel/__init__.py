"""AI Operating System Kernel package.

Exposes kernel configuration, models, interfaces, exceptions, intent engine, capability resolver,
dynamic planner, resource manager, context engine, runtime coordinator, universal verifier,
event bus, OS memory, copilot integration, voice orchestrator, security guard, observability,
and central KernelEngine.
"""

import sys
from typing import Any
from app.ai.kernel.utils import lazy_import

__all__ = [
    "KernelConfiguration",
    "KernelState",
    "OperatingMode",
    "PriorityLevel",
    "IntentRequest",
    "IntentResponse",
    "ExecutionContext",
    "SystemSnapshot",
    "CapabilityMatch",
    "ExecutionPlan",
    "PlanNode",
    "VerificationResult",
    "EventRecord",
    "OSMemoryState",
    "KernelMetrics",
    "KernelHealth",
    "IKernelEngine",
    "IIntentEngine",
    "ICapabilityResolver",
    "IDynamicPlanner",
    "IResourceManager",
    "IContextEngine",
    "IRuntimeCoordinator",
    "IUniversalVerifier",
    "IEventBus",
    "IOSMemory",
    "ICopilotIntegration",
    "IVoiceOrchestrator",
    "ISecurityGuard",
    "IKernelManager",
    "KernelError",
    "IntentEngine",
    "CapabilityResolver",
    "DynamicPlanner",
    "SystemResourceManager",
    "ContextEngine",
    "RuntimeCoordinator",
    "UniversalVerifier",
    "EventBus",
    "OSMemory",
    "CopilotIntegration",
    "VoiceOrchestrator",
    "KernelSecurityGuard",
    "KernelMetricsTracker",
    "KernelHealthMonitor",
    "KernelCache",
    "MockKernelProvider",
    "KernelManager",
    "KernelEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
