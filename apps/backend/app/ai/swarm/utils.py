"""PEP 562 Lazy Import Utility Mapping for Swarm package."""

import importlib
from typing import Any

_LAZY_MAP: dict = {
    # Core Config & Models
    "SwarmConfiguration": "app.ai.swarm.configuration",
    "SwarmState": "app.ai.swarm.models",
    "AgentRole": "app.ai.swarm.models",
    "VotingStrategy": "app.ai.swarm.models",
    "ConsensusType": "app.ai.swarm.models",
    "TaskState": "app.ai.swarm.models",
    "SwarmTask": "app.ai.swarm.models",
    "SwarmAgentRecord": "app.ai.swarm.models",
    "SwarmMessage": "app.ai.swarm.models",
    "VoteRecord": "app.ai.swarm.models",
    "ConsensusDecision": "app.ai.swarm.models",
    "BlackboardEntry": "app.ai.swarm.models",
    "SwarmMissionGraph": "app.ai.swarm.models",
    "SwarmResult": "app.ai.swarm.models",
    "SwarmMetrics": "app.ai.swarm.models",
    "SwarmHealth": "app.ai.swarm.models",
    # Interfaces
    "IAgentRegistry": "app.ai.swarm.interfaces",
    "ITaskDecomposer": "app.ai.swarm.interfaces",
    "IConsensusEngine": "app.ai.swarm.interfaces",
    "ISharedBlackboard": "app.ai.swarm.interfaces",
    "ILoadBalancer": "app.ai.swarm.interfaces",
    "ISwarmEngine": "app.ai.swarm.interfaces",
    # Exceptions
    "SwarmEngineError": "app.ai.swarm.exceptions",
    "AgentAllocationError": "app.ai.swarm.exceptions",
    "ConsensusFailedError": "app.ai.swarm.exceptions",
    "TaskDecompositionError": "app.ai.swarm.exceptions",
    "BlackboardAccessError": "app.ai.swarm.exceptions",
    # Sub-systems & Managers
    "AgentRegistry": "app.ai.swarm.agent_registry",
    "CapabilityMatcher": "app.ai.swarm.capability_matcher",
    "AgentSelector": "app.ai.swarm.agent_selector",
    "AgentAllocator": "app.ai.swarm.agent_allocator",
    "TaskDecomposer": "app.ai.swarm.task_decomposer",
    "MissionGraph": "app.ai.swarm.mission_graph",
    "DependencyResolver": "app.ai.swarm.dependency_resolver",
    "ParallelExecutor": "app.ai.swarm.parallel_executor",
    "MessageBus": "app.ai.swarm.message_bus",
    "CommunicationManager": "app.ai.swarm.communication_manager",
    "NegotiationEngine": "app.ai.swarm.negotiation_engine",
    "ConsensusEngine": "app.ai.swarm.consensus_engine",
    "VotingEngine": "app.ai.swarm.voting_engine",
    "LeaderElection": "app.ai.swarm.leader_election",
    "SharedBlackboard": "app.ai.swarm.shared_blackboard",
    "SharedContext": "app.ai.swarm.shared_context",
    "SharedMemory": "app.ai.swarm.shared_memory",
    "KnowledgeSync": "app.ai.swarm.knowledge_sync",
    "ConflictResolver": "app.ai.swarm.conflict_resolver",
    "ExecutionCoordinator": "app.ai.swarm.execution_coordinator",
    "ResultAggregator": "app.ai.swarm.result_aggregator",
    "WorkflowOptimizer": "app.ai.swarm.workflow_optimizer",
    "LoadBalancer": "app.ai.swarm.load_balancer",
    "AgentHealth": "app.ai.swarm.agent_health",
    "SwarmManager": "app.ai.swarm.swarm_manager",
    "SwarmEngine": "app.ai.swarm.swarm_engine",
    # Metrics, Health, Cache & Providers
    "SwarmMetricsTracker": "app.ai.swarm.metrics",
    "SwarmHealthMonitor": "app.ai.swarm.health",
    "SwarmCache": "app.ai.swarm.cache",
    "MockSwarmProvider": "app.ai.swarm.mock_provider",
}


def lazy_import(name: str) -> Any:
    """Dynamically imports a mapped class or utility by name."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"Attribute '{name}' not found in swarm lazy mapping.")
