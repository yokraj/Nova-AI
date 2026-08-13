"""Real AI Runtime Integration & Local Model Execution Platform.

Exposes configuration, models, interfaces, exceptions, model profiles catalog, resource scheduler,
model downloader, runtime manager, specialized runtimes (LLM, Speech, TTS, Vision, OCR, Embedding,
Translation), runtime cache, monitor, observability, and central UniversalAIRuntimeEngine.
"""

import sys
from typing import Any
from app.ai.runtime.utils import lazy_import

__all__ = [
    "RuntimeConfiguration",
    "RuntimeState",
    "RuntimeStatus",
    "ModelType",
    "DeviceType",
    "QuantType",
    "ModelProfile",
    "RuntimeRequest",
    "RuntimeResponse",
    "StreamChunkResponse",
    "ResourceTelemetry",
    "DownloadProgress",
    "RuntimeHealth",
    "RuntimeMetrics",
    "IRuntimeEngine",
    "IRuntimeManager",
    "ILLMRuntime",
    "ISpeechRuntime",
    "ITTSRuntime",
    "IVisionRuntime",
    "IOCRRuntime",
    "IEmbeddingRuntime",
    "ITranslationRuntime",
    "IResourceScheduler",
    "IModelDownloader",
    "IRuntimeCache",
    "IRuntimeMonitor",
    "RuntimeEngineError",
    "ModelNotLoadedError",
    "ResourceAllocationError",
    "DownloadFailedError",
    "InferenceError",
    "ModelProfilesCatalog",
    "ResourceScheduler",
    "ModelDownloader",
    "RuntimeManager",
    "LLMRuntime",
    "SpeechRuntime",
    "TTSRuntime",
    "VisionRuntime",
    "OCRRuntime",
    "EmbeddingRuntime",
    "TranslationRuntime",
    "RuntimeCache",
    "RuntimeMonitor",
    "RuntimeMetricsTracker",
    "RuntimeHealthMonitor",
    "MockRuntimeProvider",
    "UniversalAIRuntimeEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
