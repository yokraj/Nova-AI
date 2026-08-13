"""Inference Gateway Schemas Module.

Defines Pydantic DTO request/response schemas for chat completion, streaming,
task classification, model catalog items, health, and telemetry statistics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ChatInferenceRequest(BaseModel):
    """Request schema for chat completion inference."""

    prompt: str = Field(min_length=1, description="Prompt text or conversation message")
    model: Optional[str] = Field(default=None, description="Optional target model override")
    provider: Optional[str] = Field(default=None, description="Optional target provider override")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2048, ge=1)
    system_prompt: Optional[str] = Field(default=None)
    stream: bool = Field(default=False)


class ChatInferenceResponse(BaseModel):
    """Response schema for chat completion inference."""

    request_id: str
    content: str
    model: str
    provider: str
    task_category: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    created_at: datetime


class TaskClassificationRequest(BaseModel):
    """Request schema for classifying user intent task category."""

    prompt: str = Field(min_length=1)


class TaskClassificationResponse(BaseModel):
    """Response DTO for task classification."""

    task_category: str
    detected_capabilities: List[str]
    recommended_model: str
    confidence: float


class ModelCatalogItem(BaseModel):
    """Registered AI model DTO schema."""

    model_config = ConfigDict(from_attributes=True)

    model_name: str
    provider: str
    context_window: int
    supports_vision: bool
    supports_function_calling: bool
    supports_streaming: bool
    vram_required_mb: int
    is_active: bool


class InferenceHealthResponse(BaseModel):
    """Health diagnostic report for Inference Gateway."""

    status: str = "healthy"
    providers_online_count: int
    gpu_count: int
    active_requests_count: int
    details: Dict[str, Any] = Field(default_factory=dict)


class InferenceStatisticsResponse(BaseModel):
    """Telemetry metrics report for Inference Gateway."""

    model_config = ConfigDict(from_attributes=True)

    total_requests: int
    total_tokens_processed: int
    average_ttft_ms: float
    average_tokens_per_second: float
    active_gpu_count: int
    timestamp: datetime
