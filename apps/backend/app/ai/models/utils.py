"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.models.
"""

import importlib
from typing import Any, Dict, List

_LAZY_MAP: Dict[str, str] = {
    "ModelPlatformConfiguration": "app.ai.models.configuration",
    "ModelCategory": "app.ai.models.models",
    "ModelCapability": "app.ai.models.models",
    "ModelStatus": "app.ai.models.models",
    "ModelMetadata": "app.ai.models.models",
    "ModelRoutingRequest": "app.ai.models.models",
    "ModelRoutingResponse": "app.ai.models.models",
    "GenerationRequest": "app.ai.models.models",
    "GenerationResponse": "app.ai.models.models",
    "EmbeddingRequest": "app.ai.models.models",
    "EmbeddingResponse": "app.ai.models.models",
    "AudioRequest": "app.ai.models.models",
    "AudioResponse": "app.ai.models.models",
    "VisionRequest": "app.ai.models.models",
    "VisionResponse": "app.ai.models.models",
    "PromptTemplate": "app.ai.models.models",
    "PromptMessage": "app.ai.models.models",
    "ChatRequest": "app.ai.models.models",
    "ChatResponse": "app.ai.models.models",
    "StreamChunk": "app.ai.models.models",
    "StreamingChunk": "app.ai.models.models",
    "ProviderCapability": "app.ai.models.models",
    "AIModelInfo": "app.ai.models.models",
    "ProviderHealth": "app.ai.models.models",
    "AIUsage": "app.ai.models.models",
    "ProviderMetadata": "app.ai.models.models",
    "ModelType": "app.ai.models.models",
    "ProviderType": "app.ai.models.models",
    "MessageRole": "app.ai.models.models",
    "FinishReason": "app.ai.models.models",
    "TokenUsage": "app.ai.models.models",
    "ModelMetrics": "app.ai.models.models",
    "ModelHealth": "app.ai.models.models",
    "IModelProvider": "app.ai.models.interfaces",
    "IModelRegistry": "app.ai.models.interfaces",
    "IModelRouter": "app.ai.models.interfaces",
    "ILocalModelManager": "app.ai.models.interfaces",
    "IPerformanceManager": "app.ai.models.interfaces",
    "IPromptManager": "app.ai.models.interfaces",
    "IContextManager": "app.ai.models.interfaces",
    "ITokenManager": "app.ai.models.interfaces",
    "IModelPlatformManager": "app.ai.models.interfaces",
    "IModelEngine": "app.ai.models.interfaces",
    "ModelPlatformError": "app.ai.models.exceptions",
    "UniversalModelRegistry": "app.ai.models.model_registry",
    "IntelligentModelRouter": "app.ai.models.model_router",
    "LocalModelManager": "app.ai.models.local_model_manager",
    "PerformanceManager": "app.ai.models.performance_manager",
    "PromptManager": "app.ai.models.prompt_manager",
    "ContextManager": "app.ai.models.context_manager",
    "TokenManager": "app.ai.models.token_manager",
    "ModelMetricsTracker": "app.ai.models.metrics",
    "ModelHealthMonitor": "app.ai.models.health",
    "ModelCache": "app.ai.models.cache",
    "MockModelProvider": "app.ai.models.mock_provider",
    "ModelPlatformManager": "app.ai.models.model_manager",
    "AIModelEngine": "app.ai.models.model_engine",
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
    raise AttributeError(f"module 'app.ai.models' has no attribute '{name}'")


def estimate_token_count(text: str) -> int:
    """Estimates token count for input string.

    Args:
        text: Input string.

    Returns:
        Estimated integer token count (~4 characters per token).
    """
    if not text:
        return 0
    return max(1, len(text) // 4)
