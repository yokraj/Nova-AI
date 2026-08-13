"""Pydantic V2 data models and schemas for Universal AI Orchestrator.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class ModelCategory(str, Enum):
    """Supported model functional categories."""

    CONVERSATION = "conversation"
    REASONING = "reasoning"
    CODING = "coding"
    VISION = "vision"
    SPEECH = "speech"
    TTS = "tts"
    OCR = "ocr"
    EMBEDDING = "embedding"
    TRANSLATION = "translation"
    PLANNING = "planning"
    RESEARCH = "research"
    GENERAL = "general"


class ProviderType(str, Enum):
    """Enumerate supported AI provider plugin backends."""

    OLLAMA = "ollama"
    LLAMA_CPP = "llama_cpp"
    TRANSFORMERS = "transformers"
    WHISPER = "whisper"
    PIPER = "piper"
    PADDLE_OCR = "paddle_ocr"
    REMOTE_CLUSTER = "remote_cluster"
    MOCK_SIMULATOR = "mock_simulator"


class QuantizationType(str, Enum):
    """Quantization format levels."""

    GGUF_Q4_K_M = "Q4_K_M"
    GGUF_Q8_0 = "Q8_0"
    FP16 = "FP16"
    FP32 = "FP32"
    INT8 = "INT8"


class HardwareBackend(str, Enum):
    """Hardware acceleration compute backends."""

    CUDA = "cuda"
    DIRECTML = "directml"
    CPU = "cpu"
    METAL = "metal"


class ModelSpec(BaseModel):
    """Universal AI Model Specification metadata."""

    model_id: str = Field(..., description="Unique identifier of model (e.g. qwen3:8b)")
    name: str = Field(..., description="Human-readable model name")
    category: ModelCategory = Field(ModelCategory.REASONING)
    provider_type: ProviderType = Field(ProviderType.OLLAMA)
    quantization: QuantizationType = Field(QuantizationType.GGUF_Q4_K_M)
    context_window: int = Field(8192, description="Maximum context window size in tokens")
    min_vram_mb: int = Field(4096, description="Minimum GPU VRAM requirement in MB")
    min_ram_mb: int = Field(8192, description="Minimum CPU RAM requirement in MB")
    parameters: str = Field("8B", description="Model parameter size string")
    capabilities: List[str] = Field(default_factory=list)
    license: str = Field("Apache-2.0")
    is_installed: bool = Field(True)
    is_loaded: bool = Field(False)
    version: str = Field("1.0.0")


class RoutingContext(BaseModel):
    """Input context evaluation snapshot for intelligent model routing."""

    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    prompt: str = Field(...)
    category: ModelCategory = Field(ModelCategory.REASONING)
    task_complexity: float = Field(0.5, description="Estimated task complexity 0.0 to 1.0")
    required_quality: float = Field(0.8, description="Quality requirement threshold")
    context_tokens: int = Field(1024)
    streaming_required: bool = Field(False)
    priority: str = Field("medium", description="high, medium, low")
    active_mission_id: Optional[str] = Field(None)
    active_workflow_id: Optional[str] = Field(None)


class RoutingDecision(BaseModel):
    """Calculated model selection decision result."""

    request_id: str = Field(...)
    selected_model_id: str = Field(...)
    provider_type: ProviderType = Field(ProviderType.OLLAMA)
    router_name: str = Field("ReasoningRouter")
    confidence_score: float = Field(0.95)
    fallback_models: List[str] = Field(default_factory=list)
    reason: str = Field("Optimal performance and context size match.")
    latency_ms: float = Field(5.0)


class BenchmarkScore(BaseModel):
    """Benchmark performance score evaluation snapshot."""

    model_id: str = Field(...)
    latency_ms: float = Field(120.0)
    tokens_per_second: float = Field(45.0)
    vram_used_mb: float = Field(4096.0)
    ram_used_mb: float = Field(2048.0)
    cpu_utilization_percent: float = Field(15.0)
    quality_score: float = Field(0.92, description="Output quality rating 0.0 to 1.0")
    overall_score: float = Field(0.90)
    timestamp: float = Field(default_factory=time.time)


class GPUTelemetry(BaseModel):
    """Hardware GPU resource utilization snapshot."""

    gpu_name: str = Field("NVIDIA GeForce RTX 4090")
    vram_used_mb: float = Field(3500.0)
    vram_total_mb: float = Field(24576.0)
    ram_used_mb: float = Field(8192.0)
    ram_total_mb: float = Field(32768.0)
    cpu_utilization_percent: float = Field(12.5)
    temperature_celsius: float = Field(55.0)
    active_models_loaded: List[str] = Field(default_factory=list)


class ModelDownloadProgress(BaseModel):
    """Download & installation progress snapshot."""

    model_id: str = Field(...)
    url: str = Field(...)
    bytes_downloaded: int = Field(0)
    total_bytes: int = Field(100)
    percent: float = Field(0.0)
    speed_mbps: float = Field(0.0)
    checksum_sha256: str = Field("pending")
    checksum_verified: bool = Field(False)
    status: str = Field("initiating", description="downloading, verifying, installing, ready, error")


class OrchestratorRequest(BaseModel):
    """Payload submitted to Universal AI Orchestrator APIs."""

    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    prompt: str = Field("")
    category: ModelCategory = Field(ModelCategory.REASONING)
    model_override: Optional[str] = Field(None)
    system_prompt: Optional[str] = Field(None)
    max_tokens: int = Field(2048)
    temperature: float = Field(0.7)
    stream: bool = Field(False)
    inputs: Dict[str, Any] = Field(default_factory=dict)


class OrchestratorResponse(BaseModel):
    """Payload returned by Universal AI Orchestrator APIs."""

    response_id: str = Field(default_factory=lambda: f"res_{uuid.uuid4().hex[:8]}")
    request_id: str = Field(...)
    model_id: str = Field(...)
    provider_type: ProviderType = Field(ProviderType.OLLAMA)
    text_or_data: Any = Field("")
    finish_reason: str = Field("stop")
    token_usage: Dict[str, int] = Field(default_factory=lambda: {"total_tokens": 100})
    latency_ms: float = Field(110.0)
    cached: bool = Field(False)


class StreamTokenChunk(BaseModel):
    """Real-time token chunk payload for streaming responses."""

    chunk_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:8]}")
    request_id: str = Field(...)
    model_id: str = Field(...)
    delta_text: str = Field(...)
    token_index: int = Field(0)
    is_final: bool = Field(False)


class OrchestratorHealth(BaseModel):
    """Diagnostic health snapshot of orchestrator layer."""

    is_healthy: bool = Field(True)
    status: str = Field("HEALTHY")
    installed_models_count: int = Field(8)
    loaded_models_count: int = Field(3)
    active_providers: List[str] = Field(default_factory=lambda: ["ollama", "whisper", "piper"])
    telemetry: GPUTelemetry = Field(default_factory=GPUTelemetry)
    timestamp: float = Field(default_factory=time.time)
