"""Core schemas and request/response models for the Nova AI Gateway.

Defines Pydantic v2 data models for message structures, config payloads,
and generation outputs.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


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
