"""AI Platform Models and Enums.

Defines Pydantic v2 data models, schemas, and enums representing the core domain contracts.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ====================================================
# Enums
# ====================================================
class ProviderType(str, Enum):
    """Supported AI provider types."""

    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    MOCK = "mock"


class ProviderCapability(str, Enum):
    """Capabilities supported by AI providers."""

    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    IMAGE = "image"
    SPEECH = "speech"
    VISION = "vision"


class ModelType(str, Enum):
    """Categorized model architectures."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"


class MessageRole(str, Enum):
    """Actor roles in chat context."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class FinishReason(str, Enum):
    """The reason model generation finished."""

    STOP = "stop"
    LENGTH = "length"
    CONTENT_FILTER = "content_filter"
    TOOL_CALLS = "tool_calls"
    ERROR = "error"


# ====================================================
# Legacy Models (Do NOT remove to preserve behavior)
# ====================================================
class PromptMessage(BaseModel):
    """Represents a chat message within an AI prompt context."""

    role: str = Field(
        ...,
        description="The role of the message sender (e.g. system, user, assistant).",
    )
    content: str = Field(..., description="The string contents of the message.")


class GenerationRequest(BaseModel):
    """Payload configuration for text generation requests."""

    model: str = Field(..., description="The name of the target model.")
    messages: List[PromptMessage] = Field(
        ..., description="The chat context list."
    )
    temperature: float = Field(
        0.7,
        ge=0.0,
        le=2.0,
        description="Controls sampling randomness (0.0 to 2.0).",
    )
    max_tokens: Optional[int] = Field(
        None, gt=0, description="The maximum number of tokens to generate."
    )
    stop_sequences: Optional[List[str]] = Field(
        None, description="Optional list of stop sequences."
    )
    stream: bool = Field(
        False, description="Whether to stream token generation chunks."
    )


class TokenUsage(BaseModel):
    """Tracks token consumption counts for a generation request."""

    prompt_tokens: int = Field(0, description="Tokens consumed by the prompt.")
    completion_tokens: int = Field(
        0, description="Tokens consumed by the completion."
    )
    total_tokens: int = Field(0, description="Total tokens consumed.")


class GenerationResponse(BaseModel):
    """Standardized output structure for text generation responses."""

    content: str = Field(..., description="Generated text content output.")
    model: str = Field(..., description="Name of the model that generated it.")
    finish_reason: str = Field(
        ..., description="Reason generation finished (e.g. stop, length)."
    )
    usage: TokenUsage = Field(
        ..., description="Token usage details for the call."
    )
    cost: float = Field(0.0, description="Estimated monetary cost in USD.")


class StreamChunk(BaseModel):
    """Represents an incremental token delta chunk for streaming responses."""

    content: str = Field(..., description="Incremental token string delta.")
    finish_reason: Optional[str] = Field(
        None, description="Reason stream finished, if applicable."
    )
    usage: Optional[TokenUsage] = Field(
        None, description="Final token usage count when finished."
    )


# ====================================================
# New AI Contracts Models
# ====================================================
class AIUsage(BaseModel):
    """Standardized model call usage and cost details."""

    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    cost: float = Field(0.0, description="Estimated USD cost of execution.")


class ChatRequest(BaseModel):
    """Payload parameter model representing a chat request."""

    messages: List[PromptMessage] = Field(..., description="Message prompts history context.")
    model: str = Field(..., description="Target model identifier.")
    temperature: float = Field(0.7, description="Controls output randomness.")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens budget limit.")
    stream: bool = Field(False, description="True if streaming is enabled.")
    stop: Optional[List[str]] = Field(None, description="Optional stop sequences list.")


class ChatResponse(BaseModel):
    """Payload returned by chat generation operations."""

    message: PromptMessage = Field(..., description="Generated message response payload.")
    finish_reason: FinishReason = Field(FinishReason.STOP, description="Completion status.")
    usage: AIUsage = Field(default_factory=AIUsage)
    model: str = Field(..., description="Model identifier used.")
    provider: str = Field(..., description="Provider name identifier.")


class EmbeddingRequest(BaseModel):
    """Parameter structure for embeddings generation queries."""

    input: List[str] = Field(..., description="Text strings list inputs to embed.")
    model: str = Field(..., description="Target embedding model identifier.")


class EmbeddingResponse(BaseModel):
    """Metadata response payload containing text vector embeddings."""

    embeddings: List[List[float]] = Field(..., description="Vector arrays representation.")
    usage: AIUsage = Field(default_factory=AIUsage)
    model: str = Field(..., description="Model identifier used.")


class StreamingChunk(BaseModel):
    """Fragment chunk structure yielded by token streaming generators."""

    content: str = Field(..., description="Text chunk string delta.")
    finish_reason: Optional[FinishReason] = None
    usage: Optional[AIUsage] = None


class ProviderHealth(BaseModel):
    """Snapshot indicating current provider latency and status."""

    is_healthy: bool = Field(True, description="True if online and responding.")
    latency_ms: float = Field(0.0, description="Latency sample duration in milliseconds.")
    status_code: int = Field(200, description="Diagnostic HTTP status code.")


class ProviderMetadata(BaseModel):
    """Telemetry detailing a provider adapter attributes."""

    name: str = Field(..., description="Unique provider identifier.")
    type: ProviderType = Field(..., description="Provider architecture type.")
    capabilities: List[ProviderCapability] = Field(..., description="Supported capabilities list.")
    models: List[str] = Field(..., description="Available model strings list.")


class AIModelInfo(BaseModel):
    """Configuration metrics describing an AI model."""

    name: str = Field(..., description="Unique model name key.")
    type: ModelType = Field(..., description="Model architecture type.")
    context_window: int = Field(..., description="Supported context window size in tokens.")
    max_output_tokens: int = Field(..., description="Limit of generated output tokens.")
    capabilities: List[ProviderCapability] = Field(default_factory=list, description="Capabilities supported by the model.")
    input_cost_per_million: float = Field(0.0, description="Cost per million input tokens in USD.")
    output_cost_per_million: float = Field(0.0, description="Cost per million output tokens in USD.")
