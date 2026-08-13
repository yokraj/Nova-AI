"""Custom exception hierarchy for Universal Skills Marketplace & SDK.
"""


class SkillEngineError(Exception):
    """Base exception for all Skills Engine errors."""

    pass


class SkillNotFoundError(SkillEngineError):
    """Raised when a requested skill is not found in local registry or marketplace."""

    pass


class PermissionDeniedError(SkillEngineError):
    """Raised when execution is blocked due to missing security permissions."""

    pass


class SkillInstallationFailedError(SkillEngineError):
    """Raised when installing or unpacking a skill package fails."""

    pass


class InvalidManifestError(SkillEngineError):
    """Raised when a skill manifest fails validation."""

    pass
