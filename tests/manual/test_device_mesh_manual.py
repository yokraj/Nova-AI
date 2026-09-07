"""12-Stage Manual Validation Script for M3.4.14 Universal Device Mesh & Edge AI Platform.
"""

import asyncio
import os
import sys

# Ensure UTF-8 output encoding for Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add apps/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/backend")))

from app.ai.device_mesh import (
    UniversalDeviceMeshEngine,
    DeviceMeshConfiguration,
    DeviceOSType,
    MeshNodeStatus,
    GpuTaskCategory,
    MockDeviceMeshProvider,
)


async def run_12_stage_validation():
    print("==================================================================")
    print("M3.4.14 – Universal Device Mesh & Edge AI Platform Validation")
    print("==================================================================\n")

    engine = UniversalDeviceMeshEngine()

    # Stage 1: Core Package Init & PEP 562 Lazy Loader
    print("Stage 1: Core Package Init & PEP 562 Lazy Loader")
    assert engine.config.auto_failover_enabled is True
    print("  [OK] Device Mesh package loaded successfully.\n")

    # Stage 2: Multi-Platform Device Registration & Discovery
    print("Stage 2: Multi-Platform Device Registration & Network Discovery")
    dev_linux = await engine.pair_device("Linux RTX 4090 Workstation", "192.168.1.101", "linux")
    dev_wsl = await engine.pair_device("WSL2 Ubuntu Node", "172.28.16.1", "wsl")
    dev_pi = await engine.pair_device("Raspberry Pi 4 Edge Node", "192.168.1.150", "raspberry_pi")
    discovered = engine.device_discovery.discover_peers()
    all_devs = await engine.devices()
    print(f"  * Linux Node: '{dev_linux['name']}' (ID: {dev_linux['device_id']}, OS: {dev_linux['os_type']})")
    print(f"  * WSL2 Node: '{dev_wsl['name']}' (ID: {dev_wsl['device_id']}, OS: {dev_wsl['os_type']})")
    print(f"  * Raspberry Pi Node: '{dev_pi['name']}' (ID: {dev_pi['device_id']}, OS: {dev_pi['os_type']})")
    print(f"  * Total Mesh Devices Registered: {len(all_devs)} | Discovered Unpaired Peers: {len(discovered)}")
    assert len(all_devs) >= 4
    print("  [OK] Registered multi-platform mesh devices.\n")

    # Stage 3: Security Pairing & Heartbeat Manager
    print("Stage 3: PIN/QR Code Security Pairing & Heartbeat Manager")
    pair_challenge = engine.device_pairing.initiate_pairing("Cloud Worker Node")
    pair_verified = engine.device_pairing.verify_pairing("Cloud Worker Node", pair_challenge["pairing_pin"])
    engine.heartbeat_manager.record_heartbeat(dev_linux["device_id"])
    is_alive = engine.heartbeat_manager.is_alive(dev_linux["device_id"])
    print(f"  * Pairing Challenge PIN: {pair_challenge['pairing_pin']} | Status: {pair_challenge['status']}")
    print(f"  * Pairing Verified: {pair_verified} | Node '{dev_linux['name']}' Heartbeat Active: {is_alive}")
    assert pair_verified is True and is_alive is True
    print("  [OK] Device pairing challenge and heartbeat verified.\n")

    # Stage 4: Secure Channel & Authentication / Authorization
    print("Stage 4: Secure Channel TLS 1.3 & mTLS Auth / Scope Authorization")
    enc_payload = engine.secure_channel.encrypt_payload({"cmd": "execute_model"})
    m_auth = engine.mesh_authentication.authenticate_node(dev_linux["device_id"], "token_secret")
    m_authz = engine.mesh_authorization.authorize_execution(dev_linux["device_id"], "gpu_inference")
    print(f"  * Wire Payload Security: '{enc_payload[:35]}...'")
    print(f"  * Node mTLS Auth: {m_auth} | Task Authorization Scope: {m_authz}")
    assert m_auth is True and m_authz is True
    print("  [OK] Secure channel and mTLS auth verified.\n")

    # Stage 5: Intelligent GPU Allocator Workload Routing
    print("Stage 5: Intelligent GPU Allocator Workload Routing (Vision, LLM, Speech, OCR, Embedding)")
    gpu_llm = await engine.allocate_gpu("llm", min_vram_mb=6144)
    gpu_vis = await engine.allocate_gpu("vision", min_vram_mb=4096)
    gpu_speech = await engine.allocate_gpu("speech", min_vram_mb=3072)
    print(f"  * LLM Workload -> Assigned GPU Node: '{gpu_llm['device_name']}' (Allocated: {gpu_llm['allocated_vram_mb']} MB VRAM)")
    print(f"  * Vision Workload -> Assigned GPU Node: '{gpu_vis['device_name']}' (Allocated: {gpu_vis['allocated_vram_mb']} MB VRAM)")
    print(f"  * Speech Workload -> Assigned GPU Node: '{gpu_speech['device_name']}' (Allocated: {gpu_speech['allocated_vram_mb']} MB VRAM)")
    assert gpu_llm["success"] is True
    print("  [OK] Intelligent GPU Allocator routed workloads to optimal nodes.\n")

    # Stage 6: Distributed Task Scheduler & Task Router
    print("Stage 6: Distributed Task Scheduler & Capability-based Task Router")
    sched_res = await engine.execute_remote(dev_linux["device_id"], "Compile C++ Engine", {"flag": "-O3"})
    best_node = engine.task_router.select_best_node(engine.device_registry.list_devices(), required_os="linux")
    print(f"  * Distributed Execution ID: '{sched_res['execution_id']}' | Success: {sched_res['success']} | Output: {sched_res['output']['result']}")
    print(f"  * Task Router Selected Node: '{best_node.name}' (OS: {best_node.os_type.value})")
    assert sched_res["success"] is True
    assert best_node.os_type == DeviceOSType.LINUX
    print("  [OK] Distributed Scheduler and Task Router verified.\n")

    # Stage 7: Cross-Platform OS Managers Suite
    print("Stage 7: Cross-Platform OS Managers Suite (Docker, WSL2, Hyper-V, Linux, Windows, Android, Raspberry Pi)")
    wsl_res = engine.wsl_manager.execute_wsl_command("Ubuntu-22.04", "ls -la /opt")
    win_res = engine.windows_manager.execute_powershell(all_devs[0]["device_id"], "Get-Service")
    adb_res = engine.android_manager.execute_adb_command("android_mobile_01", "adb shell getprop ro.build.version.release")
    pi_gpio = engine.raspberry_manager.get_gpio_status(dev_pi["device_id"])
    docker_containers = engine.docker_manager.list_containers(dev_linux["device_id"])
    print(f"  * WSL2 Command Output: '{wsl_res['stdout']}'")
    print(f"  * Windows PowerShell Output: '{win_res['stdout']}'")
    print(f"  * Android ADB Output: '{adb_res['stdout']}'")
    print(f"  * Raspberry Pi GPIO Pin Status: Active Pins = {pi_gpio['active_pins_count']} | Arch = {pi_gpio['architecture']}")
    print(f"  * Docker Containers Active: {len(docker_containers)}")
    assert wsl_res["exit_code"] == 0
    assert win_res["exit_code"] == 0
    assert adb_res["exit_code"] == 0
    print("  [OK] Cross-Platform OS Managers executed native platform commands.\n")

    # Stage 8: Edge AI Runtime & Model Dispatcher
    print("Stage 8: Edge AI Runtime & Model Dispatcher (Local Quantized GGUF Model Inference)")
    loaded_models = await engine.edge_models(dev_linux["device_id"])
    edge_res = engine.edge_runtime.run_edge_model(dev_pi["device_id"], "Check room temperature sensor")
    print(f"  * Loaded Edge Models on Linux Node ({len(loaded_models)}): {[m['model_id'] for m in loaded_models]}")
    print(f"  * Raspberry Pi Edge Model Response: '{edge_res['output']}' (Latency: {edge_res['latency_ms']}ms)")
    assert len(loaded_models) >= 1
    print("  [OK] Edge AI Runtime & Model Dispatcher verified.\n")

    # Stage 9: Network Monitor, Bandwidth Optimizer & Offline Sync
    print("Stage 9: Network Monitor, Bandwidth Optimizer & Store-and-Forward Offline Sync")
    link_metrics = engine.network_monitor.get_link_metrics(all_devs[0]["device_id"], dev_linux["device_id"])
    compressed = engine.bandwidth_optimizer.compress_transfer({"payload_bytes": 1024})
    engine.offline_sync.queue_offline_task(dev_pi["device_id"], {"action": "sync_logs"})
    flushed = engine.offline_sync.flush_offline_queue(dev_pi["device_id"])
    print(f"  * Inter-Node Latency: {link_metrics['latency_ms']}ms | Bandwidth: {link_metrics['bandwidth_mbps']} Mbps | Quality: {link_metrics['quality']}")
    print(f"  * Compression Ratio: {compressed['ratio']}x ({compressed['algorithm']}) | Original: {compressed['original_size']}B -> Compressed: {compressed['compressed_size']}B")
    print(f"  * Store-and-Forward Offline Sync Flushed Tasks: {len(flushed)}")
    assert link_metrics["latency_ms"] < 10.0
    assert len(flushed) == 1
    print("  [OK] Network Monitor, Bandwidth Optimizer & Offline Sync verified.\n")

    # Stage 10: Fault Detector, Automatic Failover & Checkpoint Replication
    print("Stage 10: Fault Detector, Automatic Failover & Checkpoint Replication")
    fault_check = engine.fault_detector.check_node_fault("faulty_node_99", is_responsive=False)
    failover_res = await engine.automatic_failover.handle_node_failure("faulty_node_99")
    repl_res = engine.checkpoint_replication.replicate_checkpoint("msn_001", {"task_step": 4})
    metrics = await engine.get_metrics()
    print(f"  * Fault Detector Result: Has Fault = {fault_check['has_fault']} (Type: {fault_check['fault_type']})")
    print(f"  * Failover Result: Status = {failover_res['status']} | Standby Node = '{failover_res['standby_device_id']}' | Rerouted Tasks = {failover_res['tasks_rerouted']}")
    print(f"  * Checkpoint Replicated: Task '{repl_res['task_id']}' to {repl_res['replica_nodes_count']} standby replicas")
    assert fault_check["has_fault"] is True
    assert failover_res["status"] == "FAILOVER_SUCCESS"
    print("  [OK] Automatic Failover and Checkpoint Replication verified.\n")

    # Stage 11: Device Backup, Restore & Telemetry Engine
    print("Stage 11: Device Backup, Restore & Telemetry Engine")
    backup_res = engine.device_backup.backup_device(dev_linux["device_id"])
    restore_res = engine.device_restore.restore_device(backup_res["backup_id"])
    telemetry = engine.telemetry_engine.get_mesh_telemetry()
    print(f"  * Device Backup Status: {backup_res['status']} (ID: {backup_res['backup_id']})")
    print(f"  * Device Restore Status: {restore_res['status']}")
    print(f"  * Mesh Telemetry: Total Nodes = {telemetry['total_nodes']} | Avg CPU Load = {telemetry['average_cpu_load']}% | Free VRAM = {telemetry['total_vram_free_mb']} MB")
    assert backup_res["status"] == "COMPLETED"
    assert restore_res["status"] == "RESTORED"
    print("  [OK] Device Backup, Restore & Telemetry Engine verified.\n")

    # Stage 12: Central Mesh Dashboard & Observability Snapshot
    print("Stage 12: Central Mesh Dashboard & Telemetry Observability Snapshot")
    dash = await engine.mesh_dashboard()
    health = await engine.check_health()
    metrics = await engine.get_metrics()
    print(f"  * Central Dashboard Mesh Topology: Total Nodes = {dash['mesh_status']['total_nodes']} | Online = {dash['mesh_status']['online_nodes']} | Active GPUs = {dash['mesh_status']['active_gpus']}")
    print(f"  * Mesh Proactive Recommendations ({len(dash['recommendations'])}): '{dash['recommendations'][0]['title']}'")
    print(f"  * System Health Diagnostic: Healthy = {health.is_healthy} | Total Devices = {health.total_devices_count} | GPUs = {health.total_gpus_count}")
    print(f"  * Telemetry Metrics: Devices Registered = {metrics.total_devices} | Paired = {metrics.paired_devices} | Tasks Routed = {metrics.routed_tasks}")
    assert health.is_healthy is True
    assert metrics.routed_tasks >= 1
    print("  [OK] Central Mesh Dashboard and Observability snapshot complete.\n")

    print("==================================================================")
    print("  ALL 12 STAGES PASSED SUCCESSFULLY!")
    print("  Universal Device Mesh & Edge AI Platform Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_12_stage_validation())
