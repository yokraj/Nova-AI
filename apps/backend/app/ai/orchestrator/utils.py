"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.orchestrator.
"""

import importlib
from typing import Any, Dict

_LAZY_MAP: Dict[str, str] = {
    "OrchestratorConfiguration": "app.ai.orchestrator.configuration",
    "ModelCategory": "app.ai.orchestrator.models",
    "ProviderType": "app.ai.orchestrator.models",
    "QuantizationType": "app.ai.orchestrator.models",
    "HardwareBackend": "app.ai.orchestrator.models",
    "ModelSpec": "app.ai.orchestrator.models",
    "RoutingContext": "app.ai.orchestrator.models",
    "RoutingDecision": "app.ai.orchestrator.models",
    "BenchmarkScore": "app.ai.orchestrator.models",
    "GPUTelemetry": "app.ai.orchestrator.models",
    "ModelDownloadProgress": "app.ai.orchestrator.models",
    "OrchestratorRequest": "app.ai.orchestrator.models",
    "OrchestratorResponse": "app.ai.orchestrator.models",
    "StreamTokenChunk": "app.ai.orchestrator.models",
    "OrchestratorHealth": "app.ai.orchestrator.models",
    "IProviderPlugin": "app.ai.orchestrator.interfaces",
    "IIntelligentModelRouter": "app.ai.orchestrator.interfaces",
    "IGPUScheduler": "app.ai.orchestrator.interfaces",
    "IModelInstaller": "app.ai.orchestrator.interfaces",
    "IBenchmarkEngine": "app.ai.orchestrator.interfaces",
    "IPromptOptimizer": "app.ai.orchestrator.interfaces",
    "IStreamingEngine": "app.ai.orchestrator.interfaces",
    "IUniversalAIOrchestratorEngine": "app.ai.orchestrator.interfaces",
    "OrchestratorError": "app.ai.orchestrator.exceptions",
    "ModelNotFoundError": "app.ai.orchestrator.exceptions",
    "ProviderUnavailableError": "app.ai.orchestrator.exceptions",
    "GPUOutOfMemoryError": "app.ai.orchestrator.exceptions",
    "DownloadVerificationError": "app.ai.orchestrator.exceptions",
    "OllamaAdapter": "app.ai.orchestrator.provider_plugin_framework",
    "LlamaCppAdapter": "app.ai.orchestrator.provider_plugin_framework",
    "TransformersAdapter": "app.ai.orchestrator.provider_plugin_framework",
    "WhisperAdapter": "app.ai.orchestrator.provider_plugin_framework",
    "PiperAdapter": "app.ai.orchestrator.provider_plugin_framework",
    "PaddleOCRAdapter": "app.ai.orchestrator.provider_plugin_framework",
    "RemoteGPUClusterAdapter": "app.ai.orchestrator.provider_plugin_framework",
    "ProviderPluginFactory": "app.ai.orchestrator.provider_plugin_framework",
    "GPUScheduler": "app.ai.orchestrator.gpu_scheduler",
    "ModelInstaller": "app.ai.orchestrator.model_installer",
    "BenchmarkEngine": "app.ai.orchestrator.benchmark_engine",
    "PromptOptimizer": "app.ai.orchestrator.prompt_optimizer",
    "StreamingEngine": "app.ai.orchestrator.streaming_engine",
    "HealthMonitor": "app.ai.orchestrator.health_monitor",
    "IntelligentModelRouter": "app.ai.orchestrator.intelligent_model_router",
    "OrchestratorMetricsTracker": "app.ai.orchestrator.metrics",
    "OrchestratorHealthMonitor": "app.ai.orchestrator.health",
    "OrchestratorCache": "app.ai.orchestrator.cache",
    "MockProviderAdapter": "app.ai.orchestrator.mock_provider",
    "UniversalAIOrchestratorManager": "app.ai.orchestrator.manager",
    "UniversalAIOrchestratorEngine": "app.ai.orchestrator.engine",
}


def lazy_import(name: str) -> Any:
    """Dynamically imports symbol via PEP 562 lazy mapping."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
