"""Ambient Intelligence & Continuous Voice Assistant package.

Exposes all ambient platform components via PEP 562 lazy loading so that
importing a class only triggers its module when first accessed.
"""

from typing import Any, List
from app.ai.ambient.utils import lazy_import, _LAZY_MAP


def __getattr__(name: str) -> Any:
    """Lazy loads the requested attribute dynamically."""
    return lazy_import(name)


def __dir__() -> List[str]:
    """Returns directory of all lazy loaded exports."""
    return list(_LAZY_MAP.keys())
