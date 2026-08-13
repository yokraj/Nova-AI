"""Universal Agent Workforce, Autonomous AI Company & Multi-Agent Collaboration Platform package.

Exposes configuration, models, interfaces, exceptions, message bus, task delegation engine,
peer review quality gates, shared memory, agent learning engine, voice agent orchestrator,
dashboard runtime, manager, and central UniversalAgentWorkforceEngine facade.
"""

from typing import Any
from app.ai.agents.utils import lazy_import

__all__ = [
    "WorkforceConfiguration",
    "AgentDivision",
    "AgentStatus",
    "TaskPriority",
    "TaskStatus",
    "AgentBlueprint",
    "TaskNode",
    "MissionPlanDAG",
    "PeerReviewRequest",
    "PeerReviewResult",
    "AgentMessage",
    "SharedMemoryItem",
    "AgentLearningRecord",
    "WorkforceTelemetry",
    "WorkforceHealth",
    "IAgentMessageBus",
    "ITaskDelegationEngine",
    "IPeerReviewEngine",
    "ISharedAgentMemory",
    "IAgentLearningEngine",
    "IUniversalAgentWorkforceEngine",
    "AgentWorkforceError",
    "AgentNotFoundError",
    "TaskDelegationError",
    "PeerReviewRejectedError",
    "AgentExecutionError",
    "AgentMessageBus",
    "TaskDelegationEngine",
    "PeerReviewEngine",
    "SharedAgentMemory",
    "AgentLearningEngine",
    "VoiceAgentOrchestrator",
    "WorkforceDashboardRuntime",
    "UniversalAgentWorkforceManager",
    "UniversalAgentWorkforceEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
