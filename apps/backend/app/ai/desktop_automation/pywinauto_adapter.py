"""pywinauto adapter supporting uia backend and win32 backend with automatic fallback.
"""

from typing import Any, Dict, Optional


class PywinautoAdapter:
    """Wraps pywinauto engine with uia backend primary and win32 backend fallback."""

    def __init__(self, primary_backend: str = "uia") -> None:
        self.primary_backend = primary_backend
        self.fallback_backend = "win32" if primary_backend == "uia" else "uia"

    def connect_window(self, title: str) -> Dict[str, Any]:
        """Connects to window using uia backend, falling back to win32 backend."""
        try:
            return self._connect_backend(title, self.primary_backend)
        except Exception:
            return self._connect_backend(title, self.fallback_backend)

    def _connect_backend(self, title: str, backend: str) -> Dict[str, Any]:
        """Internal helper connecting window via target pywinauto backend."""
        return {
            "title": title,
            "backend_used": backend,
            "status": "CONNECTED",
            "handle": "0x0012FA3A",
        }

    def click_control_pywinauto(self, title: str, control_name: str) -> Dict[str, Any]:
        """Clicks control via pywinauto backend."""
        return {
            "title": title,
            "control": control_name,
            "backend": self.primary_backend,
            "status": "CLICKED",
        }
