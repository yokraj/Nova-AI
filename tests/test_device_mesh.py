"""Unit and integration tests for Universal Device Mesh, Edge AI & Cross-Platform Orchestration Platform.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

from app.ai.device_mesh.engine import UniversalDeviceMeshEngine
from app.ai.device_mesh.mock_provider import MockDeviceMeshProvider
from app.ai.device_mesh.models import DeviceOSType, GpuTaskCategory, MeshNodeStatus


@pytest.mark.anyio
async def test_device_pairing_and_registry():
    engine = UniversalDeviceMeshEngine()
    paired_dev = await engine.pair_device("Linux GPU Server", "192.168.1.101", "linux")
    assert paired_dev["name"] == "Linux GPU Server"
    assert paired_dev["os_type"] == DeviceOSType.LINUX.value

    devices_list = await engine.devices()
    assert len(devices_list) >= 2


@pytest.mark.anyio
async def test_gpu_allocator_workload_routing():
    engine = UniversalDeviceMeshEngine()
    alloc_res = await engine.allocate_gpu("vision", min_vram_mb=4096)
    assert alloc_res["success"] is True
    assert alloc_res["allocated_vram_mb"] == 4096


@pytest.mark.anyio
async def test_distributed_task_execution():
    engine = UniversalDeviceMeshEngine()
    devs = await engine.devices()
    target_id = devs[0]["device_id"]

    exec_res = await engine.execute_remote(target_id, "docker_container_task", {"container": "nova/backend"})
    assert exec_res["success"] is True


@pytest.mark.anyio
async def test_platform_managers_suite():
    engine = UniversalDeviceMeshEngine()
    wsl_res = engine.wsl_manager.execute_wsl_command("Ubuntu-22.04", "uname -a")
    assert wsl_res["exit_code"] == 0

    ps_res = engine.windows_manager.execute_powershell("dev_win", "Get-Process")
    assert ps_res["exit_code"] == 0

    adb_res = engine.android_manager.execute_adb_command("dev_android", "adb devices")
    assert adb_res["exit_code"] == 0


@pytest.mark.anyio
async def test_edge_runtime_and_models():
    engine = UniversalDeviceMeshEngine()
    devs = await engine.devices()
    target_id = devs[0]["device_id"]

    models_list = await engine.edge_models(target_id)
    assert len(models_list) >= 1

    edge_res = engine.edge_runtime.run_edge_model(target_id, "Summarize system state")
    assert "Edge Runtime" in edge_res["output"]


@pytest.mark.anyio
async def test_automatic_failover_and_checkpoint():
    engine = UniversalDeviceMeshEngine()
    failover_res = await engine.automatic_failover.handle_node_failure("node_failed_01")
    assert failover_res["status"] == "FAILOVER_SUCCESS"

    repl_res = engine.checkpoint_replication.replicate_checkpoint("task_001", {"step": 2})
    assert repl_res["status"] == "REPLICATED"


@pytest.mark.anyio
async def test_mesh_dashboard_and_status():
    engine = UniversalDeviceMeshEngine()
    dash = await engine.mesh_dashboard()
    assert "mesh_status" in dash
    assert "telemetry" in dash
    assert len(dash["recommendations"]) >= 1


@pytest.mark.anyio
async def test_mesh_health_and_metrics():
    engine = UniversalDeviceMeshEngine()
    await engine.pair_device("WSL Node", "172.28.16.1", "wsl")

    health = await engine.check_health()
    assert health.is_healthy is True
    assert health.total_devices_count >= 2

    metrics = await engine.get_metrics()
    assert metrics.total_devices >= 1


@pytest.mark.anyio
async def test_mock_device_mesh_provider():
    mock = MockDeviceMeshProvider()
    dev = await mock.mock_pair_device("Mock Node")
    assert dev.name == "Mock Node"

    gpu_alloc = await mock.mock_allocate_gpu()
    assert gpu_alloc.success is True
