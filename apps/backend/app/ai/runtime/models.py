"""Pydantic data models, enums, and schemas for Real AI Runtime Integration & Execution Platform.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class RuntimeState(str, Enum):
    """Enumerate model runtime load states."""

    UNLOADED = "UNLOADED"
    LOADING = "LOADING"
    READY = "READY"
    INFERRING = "INFERRING"
    SUSPENDED = "SUSPENDED"
    ERROR = "ERROR"


class RuntimeStatus(str, Enum):
    """Enumerate overall runtime platform health statuses."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"


class ModelType(str, Enum):
    """Enumerate model categories supported by execution runtimes."""

    LLM = "llm"
    REASONING = "reasoning"
    CODING = "coding"
    SPEECH = "speech"
    TTS = "tts"
    VISION = "vision"
    OCR = "ocr"
    EMBEDDING = "embedding"
    TRANSLATION = "translation"


class ModelCapability(str, Enum):
    """Enumerate model capability types."""

    CODE_GENERATION = "code_generation"
    TEXT_GENERATION = "text_generation"
    REASONING = "reasoning"
    VISION_UNDERSTANDING = "vision_understanding"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    EMBEDDINGS = "embeddings"
    OCR = "ocr"


class DeviceType(str, Enum):
    """Enumerate hardware compute backends."""

    CUDA = "cuda"
    CPU = "cpu"
    DIRECTML = "directml"
    METAL = "metal"
    MPS = "mps"


class QuantType(str, Enum):
    """Enumerate model quantization formats."""

    GGUF_Q4_K_M = "GGUF_Q4_K_M"
    GGUF_Q8_0 = "GGUF_Q8_0"
    FP16 = "FP16"
    FP32 = "FP32"
    INT8 = "INT8"


class ModelProfile(BaseModel):
    """Profile specification for local AI model weights."""

    model_id: str = Field(...)
    name: str = Field(...)
    type: ModelType = Field(ModelType.LLM)
    quant: QuantType = Field(QuantType.GGUF_Q4_K_M)
    min_vram_mb: int = Field(4096)
    min_ram_mb: int = Field(8192)
    context_length: int = Field(8192)
    latency_ms: float = Field(150.0)
    recommended_tasks: List[str] = Field(default_factory=list)
    license: str = Field("Apache-2.0")


class LocalModelInfo(BaseModel):
    """Legacy compatibility model info schema."""

    id: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    model_name: Optional[str] = Field(None)
    provider: str = Field("ollama")
    type: Optional[str] = Field("llm")
    context_window: Optional[int] = Field(8192)
    context_length: Optional[int] = Field(8192)
    parameters: Optional[str] = Field("8B")
    quantization: Optional[str] = Field("Q4_K_M")
    loaded_status: Optional[bool] = Field(False)
    vram_required_mb: Optional[int] = Field(4096)


class RuntimeRequest(BaseModel):
    """Inference request payload for specialized runtimes."""

    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    model_id: Optional[str] = Field(None)
    prompt: str = Field("")
    inputs: Dict[str, Any] = Field(default_factory=dict)
    max_tokens: int = Field(1024)
    temperature: float = Field(0.7)
    stream: bool = Field(False)


class RuntimeResponse(BaseModel):
    """Inference response payload from execution runtime."""

    response_id: str = Field(default_factory=lambda: f"res_{uuid.uuid4().hex[:8]}")
    model_id: str = Field(...)
    text_or_data: Any = Field("")
    finish_reason: str = Field("stop")
    token_usage: Dict[str, int] = Field(default_factory=lambda: {"total_tokens": 50})
    latency_ms: float = Field(120.0)
    device_used: DeviceType = Field(DeviceType.CUDA)

    @property
    def content(self) -> str:
        """Helper returning string representation of text_or_data."""
        return str(self.text_or_data or "")


class StreamChunkResponse(BaseModel):
    """Streaming chunk payload for token-by-token streaming."""

    chunk_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:8]}")
    model_id: str = Field(...)
    delta_text: str = Field(...)
    is_final: bool = Field(False)


class ResourceTelemetry(BaseModel):
    """Hardware resource consumption telemetry snapshot."""

    vram_used_mb: float = Field(2048.0)
    vram_total_mb: float = Field(8192.0)
    ram_used_mb: float = Field(4096.0)
    ram_total_mb: float = Field(16384.0)
    gpu_utilization_percent: float = Field(35.0)
    temperature_celsius: float = Field(52.0)

    @property
    def vram_max_mb(self) -> float:
        return self.vram_total_mb

    @property
    def ram_max_mb(self) -> float:
        return self.ram_total_mb




class DownloadProgress(BaseModel):
    """Model weights download progress metrics."""

    model_id: str = Field(...)
    bytes_downloaded: int = Field(0)
    total_bytes: int = Field(100)
    percent: float = Field(0.0)
    speed_mbps: float = Field(0.0)
    status: str = Field("downloading")


class RuntimeHealth(BaseModel):
    """Diagnostic health status for execution runtimes."""

    is_healthy: bool = Field(True)
    status: RuntimeStatus = Field(RuntimeStatus.HEALTHY)
    active_runtimes_count: int = Field(8)
    active_models: List[str] = Field(default_factory=lambda: ["qwen3:8b", "deepseek-coder:6.7b"])
    telemetry: ResourceTelemetry = Field(default_factory=ResourceTelemetry)
    timestamp: float = Field(default_factory=time.time)


class RuntimeMetrics(BaseModel):
    """Telemetry metrics snapshot for runtime platform."""

    total_inferences: int = Field(0)
    total_local_inferences: int = Field(0)
    total_fallback_inferences: int = Field(0)
    total_tokens_processed: int = Field(0)
    average_latency_ms: float = Field(0.0)
    uptime_seconds: float = Field(0.0)
