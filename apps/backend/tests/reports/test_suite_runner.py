"""Enterprise Validation Test Suite Master Runner.

Executes integration, performance, load, stress, security, and chaos test suites,
collecting pass/fail statistics and benchmarking metrics for production readiness reports.
"""

import asyncio
import sys
import time

# Ensure workspace root is in python path
sys.path.insert(0, ".")

from tests.chaos.test_dashboard_chaos import (
    test_monitoring_collector_failure_resilience,
    test_websocket_subscriber_disconnect_chaos,
)
from tests.integration.test_dashboard_integration import test_end_to_end_dashboard_pipeline
from tests.load.test_dashboard_load import test_analytics_collection_load, test_concurrent_websocket_connection_load
from tests.performance.test_dashboard_performance import (
    test_kpi_computation_performance,
    test_notification_queue_throughput,
    test_timeseries_downsampling_performance,
)
from tests.security.test_dashboard_security_hardening import (
    test_brute_force_threat_detection_trigger,
    test_rbac_privilege_escalation_prevention,
    test_websocket_spam_protection,
)
from tests.stress.test_dashboard_stress import (
    test_notification_queue_saturation_and_overflow,
    test_rate_limiter_memory_eviction_under_stress,
    test_websocket_connection_limit_stress,
)


def run_all_enterprise_validation_tests():
    """Executes all Phase M3.4.22.11 validation suites."""
    print("=====================================================================")
    print("   NOVA AI ENTERPRISE DASHBOARD VALIDATION & BENCHMARK SUITE")
    print("=====================================================================")

    passed = 0
    failed = 0
    start_total = time.time()

    def execute(name, fn, is_async=False):
        nonlocal passed, failed
        print(f"\n[TEST SUITE] Running {name}...")
        t0 = time.time()
        try:
            if is_async:
                asyncio.run(fn())
            else:
                fn()
            dur = (time.time() - t0) * 1000.0
            print(f" -> PASSED ({dur:.2f} ms)")
            passed += 1
        except Exception as exc:
            dur = (time.time() - t0) * 1000.0
            print(f" -> FAILED ({dur:.2f} ms): {exc}")
            failed += 1

    # 1. Integration Suite
    execute("End-to-End Dashboard Integration Pipeline", test_end_to_end_dashboard_pipeline, is_async=True)

    # 2. Performance Suite
    execute("TimeSeries 10k Downsampling Performance", test_timeseries_downsampling_performance)
    execute("KPI 1k Computation Performance", test_kpi_computation_performance)
    execute("Notification Queue Throughput", test_notification_queue_throughput, is_async=True)

    # 3. Load Suite
    execute("500 Concurrent WebSocket Subscriber Connection Load", test_concurrent_websocket_connection_load, is_async=True)
    execute("1,000 Parallel Analytics Telemetry Aggregations", test_analytics_collection_load, is_async=True)

    # 4. Stress Suite
    execute("Notification Queue Saturation & Bound Enforcement", test_notification_queue_saturation_and_overflow, is_async=True)
    execute("Sliding Window Rate Limiter Memory Eviction Under Stress", test_rate_limiter_memory_eviction_under_stress)
    execute("WebSocket IP Connection Limit Enforcement", test_websocket_connection_limit_stress)

    # 5. Security Suite
    execute("RBAC Privilege Escalation Prevention", test_rbac_privilege_escalation_prevention)
    execute("Brute-Force Threat Detection Alert Trigger", test_brute_force_threat_detection_trigger)
    execute("WebSocket Spam Protection Detection", test_websocket_spam_protection)

    # 6. Chaos Suite
    execute("WebSocket Subscriber Disconnect Chaos Resilience", test_websocket_subscriber_disconnect_chaos, is_async=True)
    execute("Monitoring Collector Hardware Failure Fallback", test_monitoring_collector_failure_resilience, is_async=True)

    total_time_ms = (time.time() - start_total) * 1000.0
    print("\n=====================================================================")
    print(f" SUMMARY: {passed} PASSED, {failed} FAILED across {passed + failed} Enterprise Suites ({total_time_ms:.2f} ms)")
    print("=====================================================================")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_enterprise_validation_tests()
