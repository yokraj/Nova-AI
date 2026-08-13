"""Execution Context maintains session parameters and variables during execution.
"""

from typing import Dict, Any, Optional
from uuid import uuid4

class ExecutionContext:
    """Provides intermediate state storage for action steps execution."""

    def __init__(self, session_id: Optional[str] = None) -> None:
        self.session_id = session_id or str(uuid4())[:8]
        self.variables: Dict[str, Any] = {}
        self.active_window_title: Optional[str] = None
        self.active_pid: Optional[int] = None
