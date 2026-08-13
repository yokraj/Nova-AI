"""Enterprise Intelligent Planner & Decomposition Engine - lazy package exports.
"""

from __future__ import annotations

import sys
from importlib import import_module
from typing import Any

# Maps public API names to internal module paths
_EXPORTS = {
    "LocalPlannerEngine": "app.ai.planner.planner",
    "MultiAgentPlannerConfiguration": "app.ai.planner.configuration",
    "PlanningRequest": "app.ai.planner.models",
    "PlanningResponse": "app.ai.planner.models",
    "Goal": "app.ai.planner.models",
    "TaskTree": "app.ai.planner.models",
    "DependencyGraph": "app.ai.planner.models",
    "ExecutionPlan": "app.ai.planner.models",
    "PlannerError": "app.ai.planner.exceptions",
    "CycleError": "app.ai.planner.exceptions",
}

_CACHED_IMPORTS: dict[str, Any] = {}

def __getattr__(name: str) -> Any:
    """Dynamic package attribute retriever with lazy cache."""
    if name in _EXPORTS:
        if name not in _CACHED_IMPORTS:
            module_path = _EXPORTS[name]
            module = import_module(module_path)
            _CACHED_IMPORTS[name] = getattr(module, name)
        return _CACHED_IMPORTS[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def __dir__() -> list[str]:
    """Exposes exported members."""
    return list(_EXPORTS.keys())

__all__ = list(_EXPORTS.keys())
