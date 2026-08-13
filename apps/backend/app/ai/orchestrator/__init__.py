"""Universal Multi-Model AI Ecosystem & Intelligent AI Orchestrator package.

Exposes configuration, models, interfaces, exceptions, provider plugin framework,
GPU scheduler, model installer, benchmark engine, prompt optimizer, streaming engine,
health monitor, 10-category intelligent router, metrics, health, cache, mock provider,
manager facade, and central UniversalAIOrchestratorEngine.
"""

from typing import Any
from app.ai.orchestrator.utils import lazy_import

__all__ = [
    "OrchestratorConfiguration",
    "ModelCategory",
    "ProviderType",
    "QuantizationType",
    "HardwareBackend",
    "ModelSpec",
    "RoutingContext",
    "RoutingDecision",
    "BenchmarkScore",
    "GPUTelemetry",
    "ModelDownloadProgress",
    "OrchestratorRequest",
    "OrchestratorResponse",
    "StreamTokenChunk",
    "OrchestratorHealth",
    "IProviderPlugin",
    "IIntelligentModelRouter",
    "IGPUScheduler",
    "IModelInstaller",
    "IBenchmarkEngine",
    "IPromptOptimizer",
    "IStreamingEngine",
    "IUniversalAIOrchestratorEngine",
    "OrchestratorError",
    "ModelNotFoundError",
    "ProviderUnavailableError",
    "GPUOutOfMemoryError",
    "DownloadVerificationError",
    "OllamaAdapter",
    "LlamaCppAdapter",
    "TransformersAdapter",
    "WhisperAdapter",
    "PiperAdapter",
    "PaddleOCRAdapter",
    "RemoteGPUClusterAdapter",
    "ProviderPluginFactory",
    "GPUScheduler",
    "ModelInstaller",
    "BenchmarkEngine",
    "PromptOptimizer",
    "StreamingEngine",
    "HealthMonitor",
    "IntelligentModelRouter",
    "OrchestratorMetricsTracker",
    "OrchestratorHealthMonitor",
    "OrchestratorCache",
    "MockProviderAdapter",
    "UniversalAIOrchestratorManager",
    "UniversalAIOrchestratorEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
