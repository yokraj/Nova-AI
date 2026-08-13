"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.agents.
"""

import importlib
from typing import Any, Dict

_LAZY_MAP: Dict[str, str] = {
    "WorkforceConfiguration": "app.ai.agents.configuration",
    "AgentDivision": "app.ai.agents.models",
    "AgentStatus": "app.ai.agents.models",
    "TaskPriority": "app.ai.agents.models",
    "TaskStatus": "app.ai.agents.models",
    "AgentBlueprint": "app.ai.agents.models",
    "TaskNode": "app.ai.agents.models",
    "MissionPlanDAG": "app.ai.agents.models",
    "PeerReviewRequest": "app.ai.agents.models",
    "PeerReviewResult": "app.ai.agents.models",
    "AgentMessage": "app.ai.agents.models",
    "SharedMemoryItem": "app.ai.agents.models",
    "AgentLearningRecord": "app.ai.agents.models",
    "WorkforceTelemetry": "app.ai.agents.models",
    "WorkforceHealth": "app.ai.agents.models",
    "IAgentMessageBus": "app.ai.agents.interfaces",
    "ITaskDelegationEngine": "app.ai.agents.interfaces",
    "IPeerReviewEngine": "app.ai.agents.interfaces",
    "ISharedAgentMemory": "app.ai.agents.interfaces",
    "IAgentLearningEngine": "app.ai.agents.interfaces",
    "IUniversalAgentWorkforceEngine": "app.ai.agents.interfaces",
    "AgentWorkforceError": "app.ai.agents.exceptions",
    "AgentNotFoundError": "app.ai.agents.exceptions",
    "TaskDelegationError": "app.ai.agents.exceptions",
    "PeerReviewRejectedError": "app.ai.agents.exceptions",
    "AgentExecutionError": "app.ai.agents.exceptions",
    "AgentMessageBus": "app.ai.agents.agent_bus",
    "TaskDelegationEngine": "app.ai.agents.delegation_engine",
    "PeerReviewEngine": "app.ai.agents.peer_review_engine",
    "SharedAgentMemory": "app.ai.agents.shared_memory",
    "AgentLearningEngine": "app.ai.agents.agent_learning_engine",
    "VoiceAgentOrchestrator": "app.ai.agents.voice_orchestrator",
    "WorkforceDashboardRuntime": "app.ai.agents.dashboard_runtime",
    "UniversalAgentWorkforceManager": "app.ai.agents.manager",
    "UniversalAgentWorkforceEngine": "app.ai.agents.engine",
}


def lazy_import(name: str) -> Any:
    """Dynamically imports symbol via PEP 562 lazy mapping."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
