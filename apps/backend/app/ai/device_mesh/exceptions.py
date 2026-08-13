"""Custom exception hierarchy for Universal Device Mesh, Edge AI & Cross-Platform Orchestration Platform.
"""


class DeviceMeshError(Exception):
    """Base exception for all Device Mesh errors."""

    pass


class DeviceNotFoundError(DeviceMeshError):
    """Raised when target device ID does not exist in registry."""

    pass


class DevicePairingError(DeviceMeshError):
    """Raised when device security pairing handshake fails."""

    pass


class GpuAllocationError(DeviceMeshError):
    """Raised when no suitable GPU node with requested VRAM is available."""

    pass


class MeshNodeUnreachableError(DeviceMeshError):
    """Raised when mesh node fails heartbeat check or connection times out."""

    pass
