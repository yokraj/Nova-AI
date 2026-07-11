"""Span representing individual segments inside trace graphs.
"""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field


class Span(BaseModel):
    """Execution span representing an individual task segment in trace graphs."""

    trace_id: uuid.UUID
    span_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    parent_span_id: Optional[uuid.UUID] = None
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
