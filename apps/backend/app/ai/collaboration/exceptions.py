"""Custom exception classes for the Agent Collaboration & Communication Engine.
"""

class CollaborationError(Exception):
    """Base error for all collaboration engine operations."""
    pass

class RoutingError(CollaborationError):
    """Raised when message routing rules fail or target agents cannot be resolved."""
    pass

class ConsensusFailure(CollaborationError):
    """Raised when the consensus engine fails to reach agreement."""
    pass

class NegotiationError(CollaborationError):
    """Raised when task bidding or agent workload negotiations fail."""
    pass

class HandoffError(CollaborationError):
    """Raised when a task transfer or context handoff fails."""
    pass
