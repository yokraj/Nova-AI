"""PEP 562 Lazy Import Utility Mapping.
"""

import importlib
from typing import Any

_LAZY_MAP = {
    "CollaborationEngine": "app.ai.collaboration.collaboration_engine",
    "CommunicationBus": "app.ai.collaboration.communication_bus",
    "MessageRouter": "app.ai.collaboration.message_router",
    "ConversationManager": "app.ai.collaboration.conversation_manager",
    "NegotiationEngine": "app.ai.collaboration.negotiation_engine",
    "ConsensusEngine": "app.ai.collaboration.consensus_engine",
    "TaskHandoff": "app.ai.collaboration.task_handoff",
    "DependencyResolver": "app.ai.collaboration.dependency_resolver",
    "ConflictResolver": "app.ai.collaboration.conflict_resolution",
    "CollaborationContext": "app.ai.collaboration.collaboration_context",
    "WorkflowTracker": "app.ai.collaboration.workflow_tracker",
    "CollaborationMemory": "app.ai.collaboration.memory",
    "CollaborationMetricsTracker": "app.ai.collaboration.metrics",
    "CollaborationHealthMonitor": "app.ai.collaboration.health",
    "StructuredMessage": "app.ai.collaboration.models",
    "MessageType": "app.ai.collaboration.models",
    "MessagePriority": "app.ai.collaboration.models"
}

def lazy_import(name: str) -> Any:
    """Dynamically imports a mapped class or utility by name."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"Attribute '{name}' not found in lazy mapping configuration.")
