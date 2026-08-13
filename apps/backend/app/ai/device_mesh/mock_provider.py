"""Mock Device Mesh Provider returning deterministic test responses for offline tests and CI.
"""

from typing import Any, Dict
from app.ai.device_mesh.models import (
    DeviceOSType,
    DistributedTaskResult,
    GpuAllocationResult,
    MeshNodeDevice,
    MeshNodeStatus,
)


class MockDeviceMeshProvider:
    """Mock Device Mesh Provider returning deterministic test responses."""

    async def mock_pair_device(self, name: str) -> MeshNodeDevice:
        return MeshNodeDevice(name=name, os_type=DeviceOSType.WINDOWS, status=MeshNodeStatus.ONLINE, is_paired=True)

    async def mock_allocate_gpu(self) -> GpuAllocationResult:
        return GpuAllocationResult(
            request_id="req_mock",
            assigned_device_id="node_mock_gpu",
            device_name="Mock RTX 4090 GPU Node",
            allocated_vram_mb=4096,
            success=True,
        )

    async def mock_execute_remote(self, device_id: str) -> DistributedTaskResult:
        return DistributedTaskResult(
            execution_id="exec_mock",
            task_id="task_mock",
            assigned_device_id=device_id,
            success=True,
            output={"result": f"Executed mock remote task on {device_id}"},
            duration_sec=0.03,
        )
