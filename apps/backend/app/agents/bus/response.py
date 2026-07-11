"""AgentResponse model tracing run output parameters.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """Represents a response returned from an agent to a request."""

    success: bool = Field(..., description="True if request was processed successfully.")
    sender: str = Field(..., description="Name or identifier of the sender agent (responder).")
    receiver: str = Field(..., description="Name or identifier of the receiver agent (requester).")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Response payload parameters.")
    execution_time: float = Field(..., description="Processing execution time in seconds.")
