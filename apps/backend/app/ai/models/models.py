"""Pydantic data models, enums, and request/response structures for AI Model Integration Platform.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
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


class ModelType(str, Enum):
    """Enumerate model modality types."""

    TEXT = "text"
    MULTIMODAL = "multimodal"
    EMBEDDING = "embedding"
    AUDIO = "audio"
    IMAGE = "image"
    CODE = "code"
    CUSTOM = "custom"



class ModelMetadata(BaseModel):
    """Universal model description and system requirements."""

    name: str = Field(...)
    model_id: Optional[str] = Field(None)
    type: ModelType = Field(ModelType.TEXT)
    category: ModelCategory = Field(ModelCategory.GENERAL)
    context_window: int = Field(4096)
    max_output_tokens: int = Field(1024)
    capabilities: List[Any] = Field(default_factory=list)
    provider_type: str = Field("ollama", description="Provider (ollama, llamacpp, transformers, whisper, piper, paddleocr, bge, openai, gemini, anthropic)")
    quantization: str = Field("Q4_K_M", description="Quantization level (e.g. Q4_K_M, FP16, INT8)")
    vram_mb: int = Field(2048, description="Estimated GPU VRAM requirement in MB")
    ram_mb: int = Field(4096, description="Estimated CPU RAM requirement in MB")
    version: str = Field("1.0.0")
    license: str = Field("Open Source")
    priority: int = Field(1, description="Higher integer means preferred model for category")
    status: ModelStatus = Field(ModelStatus.READY)

    def model_post_init(self, __context: Any) -> None:
        if not self.model_id:
            self.model_id = self.name



class ModelRoutingRequest(BaseModel):
    """Request payload submitted to Intelligent Model Router."""

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    prompt: str = Field(...)
    category: ModelCategory = Field(ModelCategory.GENERAL, alias="task_category")
    preferred_model: Optional[str] = Field(None, description="Optional preferred model ID override")

    @property
    def task_category(self) -> ModelCategory:
        return self.category




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

    prompt: str = Field("")
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

    text_list: List[str] = Field(default_factory=list)
    model_id: Optional[str] = Field(None)

    def __init__(self, **data: Any) -> None:
        if "input" in data and "text_list" not in data:
            val = data["input"]
            data["text_list"] = val if isinstance(val, list) else [val]
        super().__init__(**data)


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


class MessageRole(str, Enum):
    """Message sender role in multi-turn chat interactions."""

    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"


class FinishReason(str, Enum):
    """Reason for completion termination."""

    STOP = "stop"
    LENGTH = "length"
    TOOL_CALLS = "tool_calls"
    CONTENT_FILTER = "content_filter"


class PromptMessage(BaseModel):
    """Prompt message model for multi-turn chat conversations."""

    role: MessageRole = Field(MessageRole.USER, description="Message sender role (user, system, assistant)")
    content: str = Field("", description="Message text content")


class ChatRequest(BaseModel):
    """Chat request payload for multi-turn conversations."""

    messages: List[PromptMessage] = Field(default_factory=list)
    model: Optional[str] = Field(None)
    temperature: float = Field(0.7)
    max_tokens: int = Field(1024)


class ChatResponse(BaseModel):
    """Chat response payload."""

    message: PromptMessage = Field(default_factory=lambda: PromptMessage(role=MessageRole.ASSISTANT, content=""))
    finish_reason: FinishReason = Field(FinishReason.STOP)
    model: str = Field("qwen3:8b")

    @property
    def text(self) -> str:
        return self.message.content


class StreamChunk(BaseModel):
    """Streaming response token chunk model."""

    text: str = Field("")
    finish_reason: Optional[str] = Field(None)

    def __init__(self, **data: Any) -> None:
        if "content" in data and "text" not in data:
            data["text"] = data["content"]
        super().__init__(**data)

    @property
    def content(self) -> str:
        return self.text


class ModelHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    status_code: int = Field(200)
    status: str = Field("healthy")
    active_models_count: int = Field(1)
    loaded_models: List[str] = Field(default_factory=list)
    total_vram_used_mb: int = Field(2048)
    timestamp: float = Field(default_factory=time.time)


class ProviderType(str, Enum):
    """Enumerate the types of AI providers supported by the gateway."""

    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    MOCK = "mock"
    LLAMACPP = "llamacpp"
    TRANSFORMERS = "transformers"
    WHISPER = "whisper"
    PIPER = "piper"
    PADDLEOCR = "paddleocr"
    BGE = "bge"


class ProviderCapability(str, Enum):
    """Enumerate the capabilities supported by AI providers."""

    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    IMAGE = "image"
    SPEECH = "speech"
    VISION = "vision"
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    VISION_UNDERSTANDING = "vision_understanding"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    OCR = "ocr"
    REASONING = "reasoning"


StreamingChunk = StreamChunk
AIModelInfo = ModelMetadata
ProviderHealth = ModelHealth
AIUsage = TokenUsage
ProviderMetadata = ModelMetadata




