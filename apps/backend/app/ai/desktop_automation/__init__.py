"""Universal Desktop, Browser & Operating System Automation Engine package.

Uses PEP 562 lazy loading for optimal initialization overhead.
"""

from typing import Any
from app.ai.desktop_automation.utils import _LAZY_MAP, lazy_import


def __getattr__(name: str) -> Any:
    """Lazy loads symbols on attribute access."""
    return lazy_import(name)


def __dir__() -> list[str]:
    """Returns list of all available symbols for autocompletion."""
    return list(_LAZY_MAP.keys())
