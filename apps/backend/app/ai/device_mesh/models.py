"""Pydantic data models, enums, and schemas for Universal Device Mesh & Edge AI.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class DeviceOSType(str, Enum):
    """Enumerate node operating system and container platforms."""

    WINDOWS = "windows"
    LINUX = "linux"
    WSL = "wsl"
    DOCKER = "docker"
    VM = "vm"
    ANDROID = "android"
    RASPBERRY_PI = "raspberry_pi"
    NAS = "nas"
    HOME_SERVER = "home_server"
    CLOUD_VM = "cloud_vm"


class MeshNodeStatus(str, Enum):
    """Enumerate mesh node connectivity status."""

    ONLINE = "online"
    OFFLINE = "offline"
    PAIRING = "pairing"
    BUSY = "busy"
    UNREACHABLE = "unreachable"
    FAULTED = "faulted"


class GpuTaskCategory(str, Enum):
    """Enumerate AI task categories for GPU routing."""

    VISION = "vision"
    LLM = "llm"
    SPEECH = "speech"
    OCR = "ocr"
    EMBEDDING = "embedding"


class MeshNodeDevice(BaseModel):
    """Mesh node device specifications and dynamic telemetry payload."""

    device_id: str = Field(default_factory=lambda: f"node_{uuid.uuid4().hex[:8]}")
    name: str = Field(...)
    os_type: DeviceOSType = Field(DeviceOSType.WINDOWS)
    ip_address: str = Field("192.168.1.100")
    status: MeshNodeStatus = Field(MeshNodeStatus.ONLINE)
    vram_total_mb: int = Field(8192)
    vram_free_mb: int = Field(6144)
    cpu_cores: int = Field(16)
    ram_total_mb: int = Field(32768)
    is_paired: bool = Field(True)
    last_heartbeat: float = Field(default_factory=time.time)


class GpuAllocationRequest(BaseModel):
    """Payload requesting GPU allocation for AI model workload."""

    request_id: str = Field(default_factory=lambda: f"gpurq_{uuid.uuid4().hex[:8]}")
    task_category: GpuTaskCategory = Field(GpuTaskCategory.LLM)
    min_vram_mb: int = Field(2048)
    preferred_os: Optional[DeviceOSType] = Field(None)


class GpuAllocationResult(BaseModel):
    """Result returned by GPU Allocator engine."""

    allocation_id: str = Field(default_factory=lambda: f"alloc_{uuid.uuid4().hex[:8]}")
    request_id: str = Field(...)
    assigned_device_id: str = Field(...)
    device_name: str = Field(...)
    allocated_vram_mb: int = Field(2048)
    success: bool = Field(True)
    error_message: Optional[str] = Field(None)


class DistributedTaskRequest(BaseModel):
    """Payload for scheduling task across the device mesh."""

    task_id: str = Field(default_factory=lambda: f"dtask_{uuid.uuid4().hex[:8]}")
    task_name: str = Field(...)
    payload: Dict[str, Any] = Field(default_factory=dict)
    required_capabilities: List[str] = Field(default_factory=list)
    timeout_sec: float = Field(60.0)


class DistributedTaskResult(BaseModel):
    """Result payload from distributed task execution."""

    execution_id: str = Field(default_factory=lambda: f"dexec_{uuid.uuid4().hex[:8]}")
    task_id: str = Field(...)
    assigned_device_id: str = Field(...)
    success: bool = Field(True)
    output: Any = Field(None)
    error_message: Optional[str] = Field(None)
    duration_sec: float = Field(0.0)
    timestamp: float = Field(default_factory=time.time)


class MeshNetworkStatus(BaseModel):
    """Mesh network topology and aggregated capacity model."""

    mesh_id: str = Field(default_factory=lambda: f"mesh_{uuid.uuid4().hex[:8]}")
    total_nodes: int = Field(0)
    online_nodes: int = Field(0)
    active_gpus: int = Field(0)
    total_vram_mb: int = Field(0)
    network_topology: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class DeviceMeshHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    total_devices_count: int = Field(0)
    online_devices_count: int = Field(0)
    total_gpus_count: int = Field(0)
    timestamp: float = Field(default_factory=time.time)


class DeviceMeshMetrics(BaseModel):
    """Telemetry collector metrics model."""

    total_devices: int = Field(0)
    paired_devices: int = Field(0)
    routed_tasks: int = Field(0)
    failover_events: int = Field(0)
    timestamp: float = Field(default_factory=time.time)
