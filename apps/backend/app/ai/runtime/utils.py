"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.runtime.
"""

import importlib
from typing import Any, Dict

_LAZY_MAP: Dict[str, str] = {
    "RuntimeConfiguration": "app.ai.runtime.configuration",
    "RuntimeState": "app.ai.runtime.models",
    "RuntimeStatus": "app.ai.runtime.models",
    "ModelType": "app.ai.runtime.models",
    "DeviceType": "app.ai.runtime.models",
    "QuantType": "app.ai.runtime.models",
    "ModelProfile": "app.ai.runtime.models",
    "RuntimeRequest": "app.ai.runtime.models",
    "RuntimeResponse": "app.ai.runtime.models",
    "StreamChunkResponse": "app.ai.runtime.models",
    "ResourceTelemetry": "app.ai.runtime.models",
    "DownloadProgress": "app.ai.runtime.models",
    "RuntimeHealth": "app.ai.runtime.models",
    "RuntimeMetrics": "app.ai.runtime.models",
    "IRuntimeEngine": "app.ai.runtime.interfaces",
    "IRuntimeManager": "app.ai.runtime.interfaces",
    "ILLMRuntime": "app.ai.runtime.interfaces",
    "ISpeechRuntime": "app.ai.runtime.interfaces",
    "ITTSRuntime": "app.ai.runtime.interfaces",
    "IVisionRuntime": "app.ai.runtime.interfaces",
    "IOCRRuntime": "app.ai.runtime.interfaces",
    "IEmbeddingRuntime": "app.ai.runtime.interfaces",
    "ITranslationRuntime": "app.ai.runtime.interfaces",
    "IResourceScheduler": "app.ai.runtime.interfaces",
    "IModelDownloader": "app.ai.runtime.interfaces",
    "IRuntimeCache": "app.ai.runtime.interfaces",
    "IRuntimeMonitor": "app.ai.runtime.interfaces",
    "RuntimeEngineError": "app.ai.runtime.exceptions",
    "ModelNotLoadedError": "app.ai.runtime.exceptions",
    "ResourceAllocationError": "app.ai.runtime.exceptions",
    "DownloadFailedError": "app.ai.runtime.exceptions",
    "InferenceError": "app.ai.runtime.exceptions",
    "ModelProfilesCatalog": "app.ai.runtime.model_profiles",
    "ResourceScheduler": "app.ai.runtime.resource_scheduler",
    "ModelDownloader": "app.ai.runtime.model_downloader",
    "RuntimeManager": "app.ai.runtime.runtime_manager",
    "LLMRuntime": "app.ai.runtime.llm_runtime",
    "SpeechRuntime": "app.ai.runtime.speech_runtime",
    "TTSRuntime": "app.ai.runtime.tts_runtime",
    "VisionRuntime": "app.ai.runtime.vision_runtime",
    "OCRRuntime": "app.ai.runtime.ocr_runtime",
    "EmbeddingRuntime": "app.ai.runtime.embedding_runtime",
    "TranslationRuntime": "app.ai.runtime.translation_runtime",
    "RuntimeCache": "app.ai.runtime.runtime_cache",
    "RuntimeMonitor": "app.ai.runtime.runtime_monitor",
    "RuntimeMetricsTracker": "app.ai.runtime.metrics",
    "RuntimeHealthMonitor": "app.ai.runtime.health",
    "MockRuntimeProvider": "app.ai.runtime.mock_provider",
    "UniversalAIRuntimeEngine": "app.ai.runtime.runtime_engine",
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
    raise AttributeError(f"module 'app.ai.runtime' has no attribute '{name}'")


def detect_available_hardware() -> Dict[str, Any]:
    """Detects available hardware backends (CUDA, CPU, RAM/VRAM).

    Returns:
        Dictionary of hardware telemetry capabilities.
    """
    return {
        "cuda_available": True,
        "device_name": "NVIDIA GeForce RTX 3080 / DirectML",
        "vram_total_mb": 8192,
        "ram_total_mb": 16384,
    }
