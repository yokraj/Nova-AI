"""Exception hierarchy for the Universal Plugin Platform."""


class PluginError(Exception):
    """Base exception for all plugin platform errors."""
    pass


class PluginNotFoundError(PluginError):
    """Raised when a requested plugin ID or capability is not found."""
    pass


class PluginLoadError(PluginError):
    """Raised when loading or instantiating a plugin fails."""
    pass


class PluginValidationError(PluginError):
    """Raised when a plugin fails manifest or structure validation."""
    pass


class PermissionDeniedError(PluginError):
    """Raised when execution is denied due to missing or unapproved permissions."""
    pass


class DependencyError(PluginError):
    """Raised when inter-plugin dependencies cannot be resolved."""
    pass


class PluginExecutionError(PluginError):
    """Raised when plugin capability execution fails at runtime."""
    pass


class SandboxViolationError(PluginError):
    """Raised when plugin execution exceeds sandbox boundaries or timeouts."""
    pass
