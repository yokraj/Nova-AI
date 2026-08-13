"""Kernel Manager high-level administrative facade for AI OS Kernel.
"""

from typing import Any, Dict, Optional
from app.ai.kernel.configuration import KernelConfiguration
from app.ai.kernel.interfaces import IKernelManager
from app.ai.kernel.models import KernelHealth, KernelState, OperatingMode


class KernelManager(IKernelManager):
    """High-level Kernel Manager controlling kernel lifecycle, configuration, and state transitions."""

    def __init__(self, config: Optional[KernelConfiguration] = None) -> None:
        self.config = config or KernelConfiguration()
        self._state = KernelState.UNINITIALIZED
        self._is_paused = False

    @property
    def state(self) -> KernelState:
        """Returns current kernel state."""
        return self._state

    @property
    def is_paused(self) -> bool:
        """Returns True if kernel is currently paused."""
        return self._is_paused

    async def start(self) -> None:
        """Starts kernel processing and sets state to IDLE."""
        self._state = KernelState.IDLE
        self._is_paused = False

    async def pause(self) -> None:
        """Pauses kernel intent processing."""
        self._is_paused = True
        self._state = KernelState.PAUSED

    async def resume(self) -> None:
        """Resumes kernel intent processing."""
        self._is_paused = False
        self._state = KernelState.IDLE

    def set_operating_mode(self, mode: OperatingMode) -> None:
        """Sets active operating mode."""
        self.config.operating_mode = mode.value if hasattr(mode, "value") else str(mode)
