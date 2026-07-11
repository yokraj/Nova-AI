"""Standardized response returned by the Enterprise AI Gateway.
"""

from pydantic import BaseModel, Field
from app.ai.models import AIUsage


class GatewayResponse(BaseModel):
    """Standardized response returned by the Enterprise AI Gateway."""

    content: str = Field(..., description="Generated text response content.")
    usage: AIUsage = Field(default_factory=AIUsage)
    provider: str = Field(..., description="Provider name identifier.")
    model: str = Field(..., description="Model identifier used.")
    finish_reason: str = Field("stop", description="Generation completion finish reason.")
    latency_ms: float = Field(0.0, description="Operation response latency duration in milliseconds.")
