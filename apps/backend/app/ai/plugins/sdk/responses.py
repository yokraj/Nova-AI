"""Standardized execution response helpers for the Plugin SDK."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PluginResult(BaseModel):
    """Helper wrapper returned by plugin capability methods."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def ok(cls, data: Any = None, **metadata: Any) -> "PluginResult":
        """Return a successful result helper."""
        return cls(success=True, data=data, metadata=metadata)

    @classmethod
    def fail(cls, error: str, **metadata: Any) -> "PluginResult":
        """Return a failed result helper."""
        return cls(success=False, error=error, metadata=metadata)
