"""Central Universal Device Mesh Engine facade unifying edge AI and cross-platform orchestration.
"""

import time
from typing import Any, Dict, List, Optional
from app.ai.device_mesh.android_manager import AndroidManager
from app.ai.device_mesh.authentication import MeshAuthentication
from app.ai.device_mesh.authorization import MeshAuthorization
from app.ai.device_mesh.automatic_failover import AutomaticFailover
from app.ai.device_mesh.bandwidth_optimizer import BandwidthOptimizer
from app.ai.device_mesh.cache import DeviceMeshCache
from app.ai.device_mesh.checkpoint_replication import CheckpointReplication
from app.ai.device_mesh.configuration import DeviceMeshConfiguration
from app.ai.device_mesh.connection_manager import ConnectionManager
from app.ai.device_mesh.container_manager import ContainerManager
from app.ai.device_mesh.device_backup import DeviceBackup
from app.ai.device_mesh.device_discovery import DeviceDiscovery
from app.ai.device_mesh.device_health import DeviceHealth
from app.ai.device_mesh.device_pairing import DevicePairing
from app.ai.device_mesh.device_profiles import DeviceProfiles
from app.ai.device_mesh.device_registry import DeviceRegistry
from app.ai.device_mesh.device_restore import DeviceRestore
from app.ai.device_mesh.distributed_scheduler import DistributedScheduler
from app.ai.device_mesh.docker_manager import DockerManager
from app.ai.device_mesh.edge_runtime import EdgeRuntime
from app.ai.device_mesh.fault_detector import FaultDetector
from app.ai.device_mesh.gpu_allocator import GpuAllocator
from app.ai.device_mesh.health import DeviceMeshHealthMonitor
from app.ai.device_mesh.heartbeat_manager import HeartbeatManager
from app.ai.device_mesh.interfaces import IUniversalDeviceMeshEngine
from app.ai.device_mesh.linux_manager import LinuxManager
from app.ai.device_mesh.manager import DeviceMeshManagerFacade
from app.ai.device_mesh.mesh_network import MeshNetwork
from app.ai.device_mesh.metrics import DeviceMeshMetricsTracker
from app.ai.device_mesh.model_dispatcher import ModelDispatcher
from app.ai.device_mesh.models import (
    DeviceMeshHealth,
    DeviceMeshMetrics,
    DeviceOSType,
    DistributedTaskRequest,
    GpuAllocationRequest,
    GpuTaskCategory,
    MeshNodeDevice,
    MeshNodeStatus,
)
from app.ai.device_mesh.network_monitor import NetworkMonitor
from app.ai.device_mesh.offline_sync import OfflineSync
from app.ai.device_mesh.raspberry_manager import RaspberryManager
from app.ai.device_mesh.recommendation_engine import RecommendationEngine
from app.ai.device_mesh.resource_allocator import ResourceAllocator
from app.ai.device_mesh.runtime_dispatcher import RuntimeDispatcher
from app.ai.device_mesh.secure_channel import SecureChannel
from app.ai.device_mesh.session_manager import SessionManager
from app.ai.device_mesh.storage_manager import StorageManager
from app.ai.device_mesh.task_router import TaskRouter
from app.ai.device_mesh.telemetry_engine import TelemetryEngine
from app.ai.device_mesh.vm_manager import VmManager
from app.ai.device_mesh.windows_manager import WindowsManager
from app.ai.device_mesh.wsl_manager import WslManager


class UniversalDeviceMeshEngine(IUniversalDeviceMeshEngine):
    """The central Universal Device Mesh Engine facade for Nova AI."""

    def __init__(self, config: Optional[DeviceMeshConfiguration] = None) -> None:
        self.config = config or DeviceMeshConfiguration()
        self.manager_facade = DeviceMeshManagerFacade(self.config)

        self.device_registry = DeviceRegistry()
        self.device_discovery = DeviceDiscovery()
        self.device_pairing = DevicePairing()
        self.device_health = DeviceHealth()
        self.device_profiles = DeviceProfiles()

        self.connection_manager = ConnectionManager()
        self.secure_channel = SecureChannel()
        self.mesh_authentication = MeshAuthentication()
        self.mesh_authorization = MeshAuthorization()
        self.heartbeat_manager = HeartbeatManager()
        self.mesh_network = MeshNetwork()

        self.distributed_scheduler = DistributedScheduler()
        self.task_router = TaskRouter()
        self.resource_allocator = ResourceAllocator()
        self.gpu_allocator = GpuAllocator()
        self.storage_manager = StorageManager()

        self.runtime_dispatcher = RuntimeDispatcher()
        self.model_dispatcher = ModelDispatcher()
        self.container_manager = ContainerManager()
        self.docker_manager = DockerManager()
        self.wsl_manager = WslManager()
        self.vm_manager = VmManager()
        self.linux_manager = LinuxManager()
        self.windows_manager = WindowsManager()
        self.android_manager = AndroidManager()
        self.raspberry_manager = RaspberryManager()

        self.edge_runtime = EdgeRuntime()
        self.offline_sync = OfflineSync()
        self.network_monitor = NetworkMonitor()
        self.bandwidth_optimizer = BandwidthOptimizer()
        self.fault_detector = FaultDetector()
        self.automatic_failover = AutomaticFailover()
        self.checkpoint_replication = CheckpointReplication()
        self.device_backup = DeviceBackup()
        self.device_restore = DeviceRestore()
        self.telemetry_engine = TelemetryEngine()
        self.recommendation_engine = RecommendationEngine()

        self.metrics_tracker = DeviceMeshMetricsTracker()
        self.health_monitor = DeviceMeshHealthMonitor()
        self.cache = DeviceMeshCache(ttl_seconds=self.config.cache_ttl_seconds)

        # Register primary local Windows device
        primary = self.device_registry.register_device("Primary Windows Workstation", "windows", "127.0.0.1")
        self.heartbeat_manager.record_heartbeat(primary.device_id)

    async def pair_device(self, name: str, ip_address: str, os_type: str = "windows") -> Dict[str, Any]:
        """Pairs new node device into mesh network."""
        dev = self.device_registry.register_device(name, os_type, ip_address)
        self.heartbeat_manager.record_heartbeat(dev.device_id)
        self.metrics_tracker.record_device_registered()
        self.metrics_tracker.record_device_paired()
        return dev.model_dump(mode="json")

    async def remove_device(self, device_id: str) -> bool:
        """Unpairs and removes node device from mesh."""
        target = self.device_registry.get_device(device_id)
        if target:
            target.status = MeshNodeStatus.OFFLINE
            target.is_paired = False
            return True
        return False

    async def devices(self) -> List[Dict[str, Any]]:
        """Lists registered mesh node devices."""
        return [d.model_dump(mode="json") for d in self.device_registry.list_devices()]

    async def device_status(self, device_id: str) -> Dict[str, Any]:
        """Retrieves node device status telemetry."""
        target = self.device_registry.get_device(device_id) or self.device_registry.list_devices()[0]
        health_info = self.device_health.get_node_health(target.device_id)
        alive = self.heartbeat_manager.is_alive(target.device_id)
        return {
            "device_id": target.device_id,
            "name": target.name,
            "os_type": target.os_type.value,
            "ip_address": target.ip_address,
            "status": target.status.value if alive else MeshNodeStatus.UNREACHABLE.value,
            "health": health_info,
        }

    async def execute_remote(self, device_id: str, command_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes remote task on target node device."""
        req = DistributedTaskRequest(task_name=command_type, payload=payload)
        res = await self.distributed_scheduler.schedule_task(req)
        self.metrics_tracker.record_task_routed()
        return res.model_dump(mode="json")

    async def device_metrics(self, device_id: str) -> Dict[str, Any]:
        """Retrieves CPU, RAM, VRAM metrics for node."""
        target = self.device_registry.get_device(device_id) or self.device_registry.list_devices()[0]
        return {
            "device_id": target.device_id,
            "cpu_cores": target.cpu_cores,
            "ram_total_mb": target.ram_total_mb,
            "vram_total_mb": target.vram_total_mb,
            "vram_free_mb": target.vram_free_mb,
        }

    async def mesh_status(self) -> Dict[str, Any]:
        """Retrieves aggregated mesh network topology status."""
        total = len(self.device_registry.list_devices())
        status = self.mesh_network.get_mesh_status(total, total)
        return status.model_dump(mode="json")

    async def allocate_gpu(self, task_category: str, min_vram_mb: int = 2048) -> Dict[str, Any]:
        """Routes task category to best available GPU node."""
        cat = GpuTaskCategory.LLM
        try:
            cat = GpuTaskCategory(task_category.lower())
        except ValueError:
            pass

        req = GpuAllocationRequest(task_category=cat, min_vram_mb=min_vram_mb)
        res = self.gpu_allocator.allocate_gpu(req)
        return res.model_dump(mode="json")

    async def edge_models(self, device_id: str) -> List[Dict[str, Any]]:
        """Lists loaded edge AI models on target node."""
        return self.model_dispatcher.get_loaded_models(device_id)

    async def mesh_dashboard(self) -> Dict[str, Any]:
        """Returns central mesh dashboard metrics snapshot."""
        mesh_st = await self.mesh_status()
        telemetry = self.telemetry_engine.get_mesh_telemetry()
        recs = self.recommendation_engine.generate_recommendations()
        return {
            "mesh_status": mesh_st,
            "telemetry": telemetry,
            "recommendations": recs,
        }

    async def check_health(self) -> DeviceMeshHealth:
        """Retrieves device mesh health diagnostics."""
        all_devs = self.device_registry.list_devices()
        return self.health_monitor.check_health(len(all_devs), len(all_devs), len(all_devs))

    async def get_metrics(self) -> DeviceMeshMetrics:
        """Retrieves telemetry metrics."""
        return self.metrics_tracker.get_metrics()
