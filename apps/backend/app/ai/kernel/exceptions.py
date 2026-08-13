"""Custom exception hierarchy for AI OS Kernel.
"""


class KernelError(Exception):
    """Base exception for all AI OS Kernel errors."""

    pass


class IntentParsingError(KernelError):
    """Raised when Universal Intent Engine fails to parse natural language query."""

    pass


class CapabilityResolutionError(KernelError):
    """Raised when system capability resolution fails."""

    pass


class PlanningError(KernelError):
    """Raised when Dynamic Planner fails to build an execution DAG."""

    pass


class ResourceExhaustedError(KernelError):
    """Raised when hardware or model resources are exhausted."""

    pass


class SecurityApprovalRequiredError(KernelError):
    """Raised when sensitive action requires explicit user approval."""

    pass


class ExecutionFailedError(KernelError):
    """Raised when runtime step execution encounters unrecoverable failure."""

    pass


class VerificationFailedError(KernelError):
    """Raised when post-execution verification fails after all recovery attempts."""

    pass


class KernelStateError(KernelError):
    """Raised when kernel is invoked in an invalid state (e.g. paused or shutdown)."""

    pass
