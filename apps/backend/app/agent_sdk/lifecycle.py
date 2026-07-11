"""LifecycleManager tracking lifecycle states and callbacks of the SDK runtime.
"""

from typing import Awaitable, Callable, Optional
from app.agent_sdk.exceptions import SDKRuntimeError


class LifecycleManager:
    """Manages start, stop, and restart state transitions for Agent SDK instances."""

    def __init__(
        self,
        startup_callback: Optional[Callable[[], Awaitable[None]]] = None,
        shutdown_callback: Optional[Callable[[], Awaitable[None]]] = None,
    ) -> None:
        """Initializes LifecycleManager with transition hooks.

        Args:
            startup_callback: Async hook run on startup.
            shutdown_callback: Async hook run on shutdown.
        """
        self._startup_cb = startup_callback
        self._shutdown_cb = shutdown_callback
        self.is_running = False

    async def startup(self) -> None:
        """Starts up the SDK runtime components.

        Raises:
            SDKRuntimeError: If startup transitions fail.
        """
        if self.is_running:
            raise SDKRuntimeError("Agent SDK is already running.")
        try:
            if self._startup_cb:
                await self._startup_cb()
            self.is_running = True
        except Exception as e:
            raise SDKRuntimeError(f"SDK startup lifecycle execution failed: {str(e)}") from e

    async def shutdown(self) -> None:
        """Shuts down the SDK runtime components.

        Raises:
            SDKRuntimeError: If shutdown transitions fail.
        """
        if not self.is_running:
            return
        try:
            if self._shutdown_cb:
                await self._shutdown_cb()
            self.is_running = False
        except Exception as e:
            raise SDKRuntimeError(f"SDK shutdown lifecycle execution failed: {str(e)}") from e

    async def restart(self) -> None:
        """Restarts the SDK runtime components."""
        await self.shutdown()
        await self.startup()
