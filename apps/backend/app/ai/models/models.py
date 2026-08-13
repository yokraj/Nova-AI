"""Pydantic data models, enums, and request/response structures for AI Model Integration Platform.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class ModelCategory(str, Enum):
    """Enumerate AI model task classifications."""

    CODING = "coding"
    VISION = "vision"
    SPEECH = "speech"
    TTS = "tts"
    EMBEDDING = "embedding"
    REASONING = "reasoning"
    PLANNING = "planning"
    RESEARCH = "research"
    SOFTWARE_ENGINEERING = "software_engineering"
    OCR = "ocr"
    TRANSLATION = "translation"
    GENERAL = "general"


class ModelCapability(str, Enum):
    """Enumerate specific model functional capabilities."""

    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    VISION_UNDERSTANDING = "vision_understanding"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    EMBEDDINGS = "embeddings"
    OCR = "ocr"
    REASONING = "reasoning"


class ModelStatus(str, Enum):
    """Enumerate runtime load state of a model."""

    UNLOADED = "UNLOADED"
    LOADING = "LOADING"
    READY = "READY"
    IN_USE = "IN_USE"
    ERROR = "ERROR"


class ModelMetadata(BaseModel):
    """Universal model description and system requirements."""

    model_id: str = Field(...)
    name: str = Field(...)
    category: ModelCategory = Field(ModelCategory.GENERAL)
    capabilities: List[ModelCapability] = Field(default_factory=list)
    provider_type: str = Field("ollama", description="Provider (ollama, llamacpp, transformers, whisper, piper, paddleocr, bge, openai, gemini, anthropic)")
    quantization: str = Field("Q4_K_M", description="Quantization level (e.g. Q4_K_M, FP16, INT8)")
    vram_mb: int = Field(2048, description="Estimated GPU VRAM requirement in MB")
    ram_mb: int = Field(4096, description="Estimated CPU RAM requirement in MB")
    version: str = Field("1.0.0")
    license: str = Field("Open Source")
    priority: int = Field(1, description="Higher integer means preferred model for category")
    status: ModelStatus = Field(ModelStatus.READY)


class ModelRoutingRequest(BaseModel):
    """Request payload submitted to Intelligent Model Router."""

    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    prompt: str = Field(...)
    category: ModelCategory = Field(ModelCategory.GENERAL)


class ModelRoutingResponse(BaseModel):
    """Result of model routing decision."""

    request_id: str = Field(...)
    selected_model_id: str = Field(...)
    provider_type: str = Field(...)
    confidence_score: float = Field(0.95)
    fallback_used: bool = Field(False)
    latency_ms: float = Field(2.5)


class GenerationRequest(BaseModel):
    """LLM text/code generation request payload."""

    prompt: str = Field(...)
    system_prompt: Optional[str] = Field(None)
    model_id: Optional[str] = Field(None)
    max_tokens: int = Field(1024)
    temperature: float = Field(0.7)
    stream: bool = Field(False)


class TokenUsage(BaseModel):
    """Token consumption and cost accounting."""

    prompt_tokens: int = Field(0)
    completion_tokens: int = Field(0)
    total_tokens: int = Field(0)
    estimated_cost: float = Field(0.0)


class GenerationResponse(BaseModel):
    """LLM text/code generation response payload."""

    text: str = Field(...)
    finish_reason: str = Field("stop")
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    model_id: str = Field("deepseek-coder:6.7b")


class EmbeddingRequest(BaseModel):
    """Vector embedding request payload."""

    text_list: List[str] = Field(..., description="List of texts to embed")
    model_id: Optional[str] = Field(None)


class EmbeddingResponse(BaseModel):
    """Vector embedding response payload."""

    embeddings: List[List[float]] = Field(default_factory=list)
    dimensions: int = Field(768)
    token_count: int = Field(0)


class AudioRequest(BaseModel):
    """Audio STT or TTS processing request."""

    audio_bytes_or_path: Any = Field(...)
    task_type: str = Field("transcribe", description="transcribe or speak")
    language: str = Field("en")


class AudioResponse(BaseModel):
    """Audio STT or TTS response payload."""

    transcript_or_audio_path: str = Field(...)
    language: str = Field("en")


class VisionRequest(BaseModel):
    """Vision multimodal analysis request."""

    image_bytes_or_path: Any = Field(...)
    prompt: str = Field("Analyze image content")


class VisionResponse(BaseModel):
    """Vision analysis response payload."""

    description: str = Field(...)
    detected_objects: List[str] = Field(default_factory=list)
    text_found: Optional[str] = Field(None)


class PromptTemplate(BaseModel):
    """Versioned prompt template structure."""

    template_id: str = Field(...)
    name: str = Field(...)
    template_string: str = Field(...)
    version: str = Field("1.0.0")
    variables: List[str] = Field(default_factory=list)


class ModelMetrics(BaseModel):
    """Telemetry collector metrics model."""

    total_routing_requests: int = Field(0)
    local_inferences: int = Field(0)
    remote_inferences: int = Field(0)
    fallbacks_triggered: int = Field(0)
    average_latency_ms: float = Field(0.0)
    total_tokens_processed: int = Field(0)
    timestamp: float = Field(default_factory=time.time)


class PromptMessage(BaseModel):
    """Prompt message model for multi-turn chat conversations."""

    role: str = Field("user", description="Message sender role (user, system, assistant)")
    content: str = Field(..., description="Message text content")


class ChatRequest(BaseModel):
    """Chat request payload for multi-turn conversations."""

    messages: List[PromptMessage] = Field(default_factory=list)
    model: Optional[str] = Field(None)
    temperature: float = Field(0.7)
    max_tokens: int = Field(1024)


class ChatResponse(BaseModel):
    """Chat response payload."""

    message: PromptMessage = Field(default_factory=lambda: PromptMessage(role="assistant", content=""))
    finish_reason: str = Field("stop")
    model: str = Field("qwen3:8b")

    @property
    def text(self) -> str:
        return self.message.content


class StreamChunk(BaseModel):
    """Streaming response token chunk model."""

    text: str = Field(...)
    finish_reason: Optional[str] = Field(None)


class ModelHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    active_models_count: int = Field(1)
    loaded_models: List[str] = Field(default_factory=list)
    total_vram_used_mb: int = Field(2048)
    timestamp: float = Field(default_factory=time.time)


StreamingChunk = StreamChunk
ProviderCapability = ModelCapability
AIModelInfo = ModelMetadata
ProviderHealth = ModelHealth
AIUsage = TokenUsage
ProviderMetadata = ModelMetadata
ModelType = ModelCategory
MessageRole = str
FinishReason = str
