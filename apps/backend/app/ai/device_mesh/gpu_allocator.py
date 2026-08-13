"""GPU Allocator routing Vision, LLMs, Speech, OCR, and Embedding tasks to the best GPU node.
"""

from typing import List, Optional
from app.ai.device_mesh.interfaces import IGpuAllocator
from app.ai.device_mesh.models import (
    GpuAllocationRequest,
    GpuAllocationResult,
    GpuTaskCategory,
    MeshNodeDevice,
)


class GpuAllocator(IGpuAllocator):
    """Routes Vision, LLM, Speech, OCR, and Embedding workloads to the best GPU node in the mesh."""

    def __init__(self, available_nodes: Optional[List[MeshNodeDevice]] = None) -> None:
        self._nodes = available_nodes or [
            MeshNodeDevice(name="NVIDIA RTX 4090 Workstation", vram_total_mb=24576, vram_free_mb=18432),
            MeshNodeDevice(name="NVIDIA RTX 3080 Node", vram_total_mb=10240, vram_free_mb=8192),
        ]

    def allocate_gpu(self, request: GpuAllocationRequest) -> GpuAllocationResult:
        """Allocates best available GPU node for workload.

        Args:
            request: GpuAllocationRequest payload.

        Returns:
            GpuAllocationResult instance.
        """
        best = max(self._nodes, key=lambda n: n.vram_free_mb)
        return GpuAllocationResult(
            request_id=request.request_id,
            assigned_device_id=best.device_id,
            device_name=best.name,
            allocated_vram_mb=min(request.min_vram_mb, best.vram_free_mb),
            success=True,
        )
