"""Universal Multi-Model AI Integration Platform & Intelligent Model Router package.

Exposes configuration, models, interfaces, exceptions, model registry, intelligent router,
local model manager, performance manager, prompt manager, context manager, token manager,
observability, providers, and central AIModelEngine.
"""

import sys
from typing import Any
from app.ai.models.utils import lazy_import

__all__ = [
    "ModelPlatformConfiguration",
    "ModelCategory",
    "ModelCapability",
    "ModelStatus",
    "ModelMetadata",
    "ModelRoutingRequest",
    "ModelRoutingResponse",
    "GenerationRequest",
    "GenerationResponse",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "AudioRequest",
    "AudioResponse",
    "VisionRequest",
    "VisionResponse",
    "PromptTemplate",
    "PromptMessage",
    "ChatRequest",
    "ChatResponse",
    "StreamChunk",
    "StreamingChunk",
    "ProviderCapability",
    "AIModelInfo",
    "ProviderHealth",
    "AIUsage",
    "ProviderMetadata",
    "ModelType",
    "MessageRole",
    "FinishReason",
    "TokenUsage",
    "ModelMetrics",
    "ModelHealth",
    "IModelProvider",
    "IModelRegistry",
    "IModelRouter",
    "ILocalModelManager",
    "IPerformanceManager",
    "IPromptManager",
    "IContextManager",
    "ITokenManager",
    "IModelPlatformManager",
    "IModelEngine",
    "ModelPlatformError",
    "UniversalModelRegistry",
    "IntelligentModelRouter",
    "LocalModelManager",
    "PerformanceManager",
    "PromptManager",
    "ContextManager",
    "TokenManager",
    "ModelMetricsTracker",
    "ModelHealthMonitor",
    "ModelCache",
    "MockModelProvider",
    "ModelPlatformManager",
    "AIModelEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
