"""Runtime Cache wrapper for multi-modal inference responses.
"""

from typing import Any, Optional
from app.ai.runtime.runtime_cache import RuntimeCache as BaseRuntimeCache


class RuntimeCache(BaseRuntimeCache):
    """Runtime Cache wrapper."""

    pass


LocalInferenceCache = RuntimeCache

