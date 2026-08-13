"""Unit Test Suite for Nova AI System Monitoring Engine.

Tests real hardware metric collection across CPU, Memory, Disk, Network, GPU,
Process, System monitors, and SystemMonitoringEngine persistence orchestration.
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from app.monitoring.cpu import (
    CPUMonitor,
    get_cpu_count,
    get_cpu_frequency,
    get_cpu_percent_per_core,
    get_cpu_temperature,
    get_cpu_usage,
    get_load_average,
)
from app.monitoring.disk import (
    DiskMonitor,
    get_disk_io,
    get_disk_partitions,
    get_disk_usage,
    get_free_space,
)
from app.monitoring.engine import SystemMonitoringEngine
from app.monitoring.gpu import (
    GPUMonitor,
    get_gpu_devices,
    get_gpu_memory,
    get_gpu_power,
    get_gpu_temperature,
    get_gpu_usage,
)
from app.monitoring.memory import (
    MemoryMonitor,
    get_memory_percent,
    get_memory_usage,
    get_swap_usage,
    get_virtual_memory,
)
from app.monitoring.network import (
    NetworkMonitor,
    get_active_connections,
    get_hostname,
    get_ip_addresses,
    get_network_interfaces,
    get_network_io,
)
from app.monitoring.processes import (
    ProcessMonitor,
    get_process,
    get_process_count,
    get_running_processes,
    get_top_cpu_processes,
    get_top_memory_processes,
)
from app.monitoring.system import (
    SystemMonitor,
    get_architecture,
    get_boot_time,
    get_environment,
    get_kernel,
    get_machine,
    get_os,
    get_python_version,
    get_system_information,
    get_uptime,
)


def test_cpu_monitor():
    """Test real CPU hardware monitoring functions."""
    monitor = CPUMonitor()
    usage = monitor.get_cpu_usage()
    assert isinstance(usage, float)
    assert usage >= 0.0

    per_core = monitor.get_cpu_percent_per_core()
    assert isinstance(per_core, list)

    freq = monitor.get_cpu_frequency()
    assert "current" in freq
    assert "min" in freq
    assert "max" in freq

    counts = monitor.get_cpu_count()
    assert counts["physical"] >= 1
    assert counts["logical"] >= 1

    temp = monitor.get_cpu_temperature()
    assert temp is None or isinstance(temp, float)

    load = monitor.get_load_average()
    assert "1min" in load
    assert "5min" in load
    assert "15min" in load

    metrics = monitor.get_metrics()
    assert "usage_percent" in metrics


def test_memory_monitor():
    """Test real Memory hardware monitoring functions."""
    monitor = MemoryMonitor()
    vm = monitor.get_virtual_memory()
    assert vm["total"] > 0
    assert vm["available"] >= 0
    assert 0.0 <= vm["percent"] <= 100.0

    usage = monitor.get_memory_usage()
    assert usage["total"] == vm["total"]

    swap = monitor.get_swap_usage()
    assert "total" in swap
    assert "used" in swap

    percent = monitor.get_memory_percent()
    assert isinstance(percent, float)

    metrics = monitor.get_metrics()
    assert "total" in metrics


def test_disk_monitor():
    """Test real Disk storage monitoring functions."""
    monitor = DiskMonitor()
    parts = monitor.get_disk_partitions()
    assert isinstance(parts, list)

    free = monitor.get_free_space("/")
    assert free["total"] >= 0

    usage = monitor.get_disk_usage()
    assert "total" in usage

    io = monitor.get_disk_io()
    assert "read_bytes" in io
    assert "write_bytes" in io

    metrics = monitor.get_metrics()
    assert "total_bytes" in metrics


def test_network_monitor():
    """Test real Network hardware monitoring functions."""
    monitor = NetworkMonitor()
    host = monitor.get_hostname()
    assert len(host) > 0

    ips = monitor.get_ip_addresses()
    assert "ipv4" in ips

    io = monitor.get_network_io()
    assert "bytes_sent" in io
    assert "bytes_recv" in io

    interfaces = monitor.get_network_interfaces()
    assert isinstance(interfaces, list)

    conns = monitor.get_active_connections()
    assert isinstance(conns, list)

    metrics = monitor.get_metrics()
    assert "hostname" in metrics


def test_gpu_monitor():
    """Test GPU monitoring functions (verifying non-crashing fallback on machines without GPU)."""
    monitor = GPUMonitor()
    devices = monitor.get_gpu_devices()
    assert isinstance(devices, list)

    usage = monitor.get_gpu_usage()
    assert isinstance(usage, list)

    temp = monitor.get_gpu_temperature()
    assert isinstance(temp, list)

    mem = monitor.get_gpu_memory()
    assert isinstance(mem, list)

    power = monitor.get_gpu_power()
    assert isinstance(power, list)

    metrics = monitor.get_metrics()
    assert isinstance(metrics, list)


def test_process_monitor():
    """Test real OS Process table monitoring functions."""
    monitor = ProcessMonitor()
    count = monitor.get_process_count()
    assert count > 0

    running = monitor.get_running_processes(limit=5)
    assert isinstance(running, list)
    assert len(running) <= 5
    if running:
        first_pid = running[0]["pid"]
        proc_detail = monitor.get_process(first_pid)
        assert proc_detail is None or proc_detail["pid"] == first_pid

    top_cpu = monitor.get_top_cpu_processes(limit=3)
    assert len(top_cpu) <= 3

    top_mem = monitor.get_top_memory_processes(limit=3)
    assert len(top_mem) <= 3

    metrics = monitor.get_metrics(limit=5)
    assert isinstance(metrics, list)


def test_system_monitor():
    """Test System OS metadata monitoring functions."""
    monitor = SystemMonitor()
    info = monitor.get_system_information()
    assert "os_name" in info
    assert "kernel" in info
    assert "machine" in info
    assert "architecture" in info
    assert "uptime_seconds" in info

    assert len(monitor.get_os()) > 0
    assert len(monitor.get_kernel()) > 0
    assert len(monitor.get_machine()) > 0
    assert len(monitor.get_architecture()) > 0
    assert isinstance(monitor.get_boot_time(), datetime)
    assert monitor.get_uptime() >= 0.0
    assert len(monitor.get_python_version()) > 0

    env = monitor.get_environment()
    assert isinstance(env, dict)


async def test_system_monitoring_engine_aggregation():
    """Test SystemMonitoringEngine complete telemetry collection and persistence workflow."""
    mock_sys_svc = AsyncMock()
    mock_res_svc = AsyncMock()
    mock_health_svc = AsyncMock()
    mock_dash_svc = AsyncMock()
    mock_analytics_svc = AsyncMock()

    mock_sys_svc.record_system_metrics.return_value = MagicMock(id=uuid.uuid4())
    mock_res_svc.record_resource_metric.return_value = MagicMock(id=uuid.uuid4())
    mock_res_svc.record_gpu_metric.return_value = MagicMock(id=uuid.uuid4())
    mock_res_svc.record_process_metric.return_value = MagicMock(id=uuid.uuid4())
    mock_health_svc.record_health.return_value = MagicMock(id=uuid.uuid4())
    mock_dash_svc.create_snapshot.return_value = MagicMock(id=uuid.uuid4())

    engine = SystemMonitoringEngine(
        system_service=mock_sys_svc,
        resource_service=mock_res_svc,
        health_service=mock_health_svc,
        dashboard_service=mock_dash_svc,
        analytics_service=mock_analytics_svc,
        config={"metrics_interval": 10},
    )

    # 1. System Metrics
    sys_rec = await engine.collect_system_metrics()
    assert sys_rec is not None
    assert mock_sys_svc.record_system_metrics.called

    # 2. Resource Metrics
    res_recs = await engine.collect_resource_metrics()
    assert len(res_recs) >= 3
    assert mock_res_svc.record_resource_metric.called

    # 3. GPU Metrics
    gpu_recs = await engine.collect_gpu_metrics()
    assert isinstance(gpu_recs, list)

    # 4. Process Metrics
    proc_recs = await engine.collect_process_metrics()
    assert isinstance(proc_recs, list)
    assert mock_res_svc.record_process_metric.called

    # 5. Health Metrics
    health_rec = await engine.collect_health_metrics()
    assert health_rec is not None
    assert mock_health_svc.record_health.called

    # 6. Dashboard Snapshot
    snapshot = await engine.collect_dashboard_snapshot()
    assert snapshot is not None
    assert mock_dash_svc.create_snapshot.called


async def test_monitoring_engine_resilience_to_collector_exceptions():
    """Test that SystemMonitoringEngine continues execution even when individual collectors raise exceptions."""
    mock_sys_svc = AsyncMock()
    mock_res_svc = AsyncMock()
    mock_health_svc = AsyncMock()
    mock_dash_svc = AsyncMock()

    mock_sys_svc.record_system_metrics.side_effect = Exception("Simulated DB connection timeout")
    mock_res_svc.record_resource_metric.return_value = MagicMock(id=uuid.uuid4())
    mock_health_svc.record_health.return_value = MagicMock(id=uuid.uuid4())
    mock_dash_svc.create_snapshot.return_value = MagicMock(id=uuid.uuid4())

    engine = SystemMonitoringEngine(
        system_service=mock_sys_svc,
        resource_service=mock_res_svc,
        health_service=mock_health_svc,
        dashboard_service=mock_dash_svc,
    )

    # System metric failure returns None cleanly without throwing unhandled exception
    res = await engine.collect_system_metrics()
    assert res is None

    # Other collectors continue to operate successfully
    res_recs = await engine.collect_resource_metrics()
    assert len(res_recs) >= 1
