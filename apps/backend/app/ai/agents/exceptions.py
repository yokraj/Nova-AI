"""Custom exception hierarchy for Universal Agent Workforce & Autonomous AI Company.
"""


class AgentWorkforceError(Exception):
    """Base exception for all agent workforce failures."""

    def __init__(self, message: str, error_code: str = "WORKFORCE_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class AgentNotFoundError(AgentWorkforceError):
    """Raised when a requested agent ID is not found in workforce registry."""

    def __init__(self, agent_id: str) -> None:
        super().__init__(f"Agent '{agent_id}' is not registered in workforce.", "AGENT_NOT_FOUND")


class TaskDelegationError(AgentWorkforceError):
    """Raised when task DAG decomposition or dependency resolution fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Task delegation failed: {reason}", "TASK_DELEGATION_FAILED")


class PeerReviewRejectedError(AgentWorkforceError):
    """Raised when a deliverable fails multi-agent peer review quality gates."""

    def __init__(self, review_id: str, comments: str) -> None:
        super().__init__(f"Peer review '{review_id}' rejected deliverable: {comments}", "PEER_REVIEW_REJECTED")


class AgentExecutionError(AgentWorkforceError):
    """Raised when an individual agent task execution encounters a failure."""

    def __init__(self, agent_id: str, task_id: str, reason: str) -> None:
        super().__init__(f"Agent '{agent_id}' failed task '{task_id}': {reason}", "AGENT_EXECUTION_FAILED")


AgentStateError = AgentExecutionError
AgentRegistrationError = AgentWorkforceError
AgentPermissionsError = AgentWorkforceError
AgentDependencyError = AgentWorkforceError




