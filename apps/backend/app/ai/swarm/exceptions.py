"""Typed exception hierarchy for Multi-Agent Collaboration & Swarm Intelligence Engine."""


class SwarmEngineError(Exception):
    """Base exception for swarm intelligence engine errors."""
    pass


class AgentAllocationError(SwarmEngineError):
    """Raised when no suitable agent can be allocated to a task."""
    pass


class ConsensusFailedError(SwarmEngineError):
    """Raised when swarm consensus voting fails to reach a decision."""
    pass


class TaskDecompositionError(SwarmEngineError):
    """Raised when goal task decomposition fails."""
    pass


class BlackboardAccessError(SwarmEngineError):
    """Raised when read/write operations on the shared blackboard fail."""
    pass
