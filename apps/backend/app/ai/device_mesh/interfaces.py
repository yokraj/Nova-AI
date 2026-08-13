"""Abstract base contracts for Universal Device Mesh, Edge AI & Cross-Platform Orchestration Platform.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.device_mesh.models import (
    DeviceMeshHealth,
    DeviceMeshMetrics,
    DistributedTaskRequest,
    DistributedTaskResult,
    GpuAllocationRequest,
    GpuAllocationResult,
    MeshNetworkStatus,
    MeshNodeDevice,
)


class IDeviceRegistry(ABC):
    """Device Registry contract for registering and managing mesh nodes."""

    @abstractmethod
    def register_device(self, name: str, os_type: str = "windows", ip_address: str = "127.0.0.1") -> MeshNodeDevice:
        """Registers new node device."""
        pass


class IGpuAllocator(ABC):
    """GPU Allocator contract for routing Vision, LLMs, Speech, OCR, and Embeddings to optimal GPUs."""

    @abstractmethod
    def allocate_gpu(self, request: GpuAllocationRequest) -> GpuAllocationResult:
        """Allocates best available GPU node for workload."""
        pass


class IDistributedScheduler(ABC):
    """Distributed Scheduler contract for scheduling tasks across the mesh."""

    @abstractmethod
    async def schedule_task(self, request: DistributedTaskRequest) -> DistributedTaskResult:
        """Schedules and dispatches task across mesh nodes."""
        pass


class IAutomaticFailover(ABC):
    """Automatic Failover contract for recovery when a mesh node fails."""

    @abstractmethod
    async def handle_node_failure(self, failed_device_id: str) -> Dict[str, Any]:
        """Triggers task failover to healthy standby node."""
        pass


class IDeviceMeshManagerFacade(ABC):
    """Subsystem Manager administrative contract."""

    @abstractmethod
    async def start(self) -> None:
        """Starts device mesh manager."""
        pass


class IUniversalDeviceMeshEngine(ABC):
    """Central Universal Device Mesh Engine facade contract."""

    @abstractmethod
    async def pair_device(self, name: str, ip_address: str, os_type: str = "windows") -> Dict[str, Any]:
        """Pairs new node device into mesh network."""
        pass

    @abstractmethod
    async def remove_device(self, device_id: str) -> bool:
        """Unpairs and removes node device from mesh."""
        pass

    @abstractmethod
    async def devices(self) -> List[Dict[str, Any]]:
        """Lists registered mesh node devices."""
        pass

    @abstractmethod
    async def device_status(self, device_id: str) -> Dict[str, Any]:
        """Retrieves node device status telemetry."""
        pass

    @abstractmethod
    async def execute_remote(self, device_id: str, command_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes remote task on target node device."""
        pass

    @abstractmethod
    async def device_metrics(self, device_id: str) -> Dict[str, Any]:
        """Retrieves CPU, RAM, VRAM metrics for node."""
        pass

    @abstractmethod
    async def mesh_status(self) -> Dict[str, Any]:
        """Retrieves aggregated mesh network topology status."""
        pass

    @abstractmethod
    async def allocate_gpu(self, task_category: str, min_vram_mb: int = 2048) -> Dict[str, Any]:
        """Routes task category to best available GPU node."""
        pass

    @abstractmethod
    async def edge_models(self, device_id: str) -> List[Dict[str, Any]]:
        """Lists loaded edge AI models on target node."""
        pass

    @abstractmethod
    async def mesh_dashboard(self) -> Dict[str, Any]:
        """Returns central mesh dashboard metrics snapshot."""
        pass
