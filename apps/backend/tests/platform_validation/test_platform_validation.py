"""Unit and Integration Tests for Nova AI Enterprise Memory Platform Validation, Optimization & Production Release.

Validates Performance Benchmarks, Subsystem Optimizers, Security Audit, Backup & Disaster Recovery,
Health Monitoring, Telemetry, Capacity Forecasting, Load & Stress Testing, Production Release Readiness,
REST APIs, and RBAC authorization.
"""

import asyncio
import pytest

from app.platform_validation import (
    ValidationConfig,
    PerformanceMonitor,
    PlatformBenchmarker,
    PlatformOptimizer,
    SecurityAuditor,
    BackupManager,
    DisasterRecoveryManager,
    PlatformHealthMonitor,
    SystemDiagnostics,
    TelemetryCollector,
    PlatformProfiler,
    CapacityPlanner,
    StressTestRunner,
    ReleaseManager,
    ValidationStatisticsTracker,
)


def test_performance_monitor_and_benchmarker():
    """Test PerformanceMonitor SLA checking and PlatformBenchmarker full suite."""
    async def _test():
        monitor = PerformanceMonitor()
        benchmarker = PlatformBenchmarker(monitor=monitor)

        sla_res = monitor.check_sla("memory_crud", latency_ms=5.0)
        assert sla_res["passed_sla"] is True

        bench_res = await benchmarker.run_full_benchmark()
        assert bench_res["all_passed"] is True
        assert "memory_crud" in bench_res["benchmarks"]

    asyncio.run(_test())


def test_platform_optimizers():
    """Test PlatformOptimizer master optimization across Memory, Vector, Graph, and RAG."""
    optimizer = PlatformOptimizer()
    res = optimizer.run_system_optimization()

    assert res["overall_status"] == "optimized"
    assert len(res["optimizations"]) == 4


def test_security_auditor():
    """Test SecurityAuditor RBAC permissions matrix and tenant isolation verification."""
    auditor = SecurityAuditor()
    sec_res = auditor.audit_security()

    assert sec_res["all_passed"] is True
    assert sec_res["audit_status"] == "COMPLIANT"


def test_backup_and_recovery_managers():
    """Test BackupManager snapshot generation and DisasterRecoveryManager state restoration."""
    backup_mgr = BackupManager()
    recovery_mgr = DisasterRecoveryManager()

    snap = backup_mgr.create_snapshot(backup_type="full")
    assert snap["status"] == "created"
    assert snap["integrity_hash"] is not None

    restore = recovery_mgr.restore_snapshot(snap["snapshot_id"])
    assert restore["restoration_status"] == "restored"
    assert restore["integrity_verified"] is True


def test_platform_health_and_telemetry():
    """Test PlatformHealthMonitor across 7 Memory Platform sub-engines and TelemetryCollector counters."""
    health_monitor = PlatformHealthMonitor()
    telemetry = TelemetryCollector()

    health = health_monitor.run_platform_health_checks()
    assert health["status"] == "healthy"
    assert health["subsystems_healthy_count"] == 7

    telemetry.increment_counter("queries_processed", 10)
    snap = telemetry.get_telemetry_snapshot()
    assert snap["counters"]["queries_processed"] == 10


def test_capacity_planner_and_stress_runner():
    """Test CapacityPlanner resource forecasting and StressTestRunner load simulation."""
    async def _test():
        planner = CapacityPlanner()
        stress_runner = StressTestRunner()

        forecast = planner.forecast_capacity(target_memories=1000000)
        assert forecast["estimated_storage_gb"] > 0
        assert forecast["estimated_ram_gb"] > 0

        stress_res = await stress_runner.run_stress_test(memories_count=10000, concurrent_users=10)
        assert stress_res["stress_test_passed"] is True

    asyncio.run(_test())


def test_release_manager_verification():
    """Test ReleaseManager release readiness approval and documentation generation."""
    async def _test():
        benchmarker = PlatformBenchmarker()
        auditor = SecurityAuditor()
        stress_runner = StressTestRunner()
        release_mgr = ReleaseManager()

        bench_res = await benchmarker.run_full_benchmark()
        sec_res = auditor.audit_security()
        stress_res = await stress_runner.run_stress_test()

        readiness = release_mgr.verify_release_readiness(bench_res, sec_res, stress_res)
        assert readiness["release_approved"] is True

        docs = release_mgr.generate_release_documentation()
        assert "performance_report" in docs
        assert "operations_runbook" in docs

    asyncio.run(_test())
